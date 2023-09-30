import collections
import datetime
import json
from collections import defaultdict
from distutils.util import strtobool
from typing import Any, Dict, List, Optional, Tuple, Union

import dateparser
import pandas as pd

from gantry.api_client import APIClient
from gantry.query.core.constants import DEFAULT_FETCH_BATCH_SIZE, SCHEMA_TYPES, TIMEZONE
from gantry.query.core.utils import _build_empty_df_with_schema

ORDER_ASCENDING = "ascending"
ORDER_DESCENDING = "descending"
DRUID_TIME_COLUMN_NAME = "__time"
TIME_COLUMN_NAME = "timestamp"


def build_base_query_params(start_time, end_time, version) -> Dict[str, Any]:
    return {
        "start_time": start_time,
        "end_time": end_time,
        "version": version,
    }


class QueryInfo(
    collections.namedtuple(
        "QueryParams", "application_node_id application version environment start_time end_time"
    )
):
    def get_base_query_params(self) -> Dict[str, Any]:
        return build_base_query_params(self.start_time, self.end_time, self.version)


def _get_raw_data(api_client: APIClient, query_info: QueryInfo, dumped_json_data: str):
    """TTL-Caches data requests to API to make
    repeated fetching operations faster.
    """
    return api_client.request(
        "POST",
        "/api/v1/applications/{}/raw_data".format(query_info.application_node_id),
        params=query_info.get_base_query_params(),
        json=json.loads(
            dumped_json_data
        ),  # Need to receive dumped data because json dicts are not hashable
        raise_for_status=True,
    )


def _get_metadata(api_client, application_name, frozen_query_params):
    # Reconstruct the query parameters as a true dictionary here, if not cached
    query_params = {k: v for k, v in frozen_query_params}
    response = api_client.request(
        "GET",
        "/api/v1/models/" + application_name + "/schemas",
        params=query_params,
        raise_for_status=True,
    )
    return response["data"]


class GantryQueryFrame(object):
    def __init__(self, api_client: APIClient, query_info: QueryInfo) -> None:
        self.api_client: APIClient = api_client
        self.query_info: QueryInfo = query_info

    @property  # type: ignore
    def metadata(self):
        # Workaround to allow for hashing of query params for caching
        frozen_query_params = frozenset(self.query_info.get_base_query_params().items())
        return _get_metadata(self.api_client, self.query_info.application, frozen_query_params)

    @property
    def _dtypes(self):
        _dtypes = {}
        metadata_property = self.metadata  # This is a property which makes an API call.
        for schema_type in SCHEMA_TYPES:
            metadata = metadata_property.get(schema_type, [])
            for column in metadata:
                column_dtype = (
                    "category"
                    if column["node_metadata"]["dtype"].get(
                        "is_categorical"
                    )  # Prevent KeyError in some cases where column['node_metadata']['dtype'] == {}
                    and not column["dtype"] == "bool"
                    else column["dtype"]
                )
                _dtypes[column["name"]] = column_dtype

        return _dtypes

    @staticmethod
    def resolve_time_strings(
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        # Convert time strings to unambiguous datetime objects.
        if isinstance(start_time, str):
            start_time_ret = dateparser.parse(start_time, settings=TIMEZONE)  # type: ignore
            if start_time_ret is None:
                raise ValueError("Invalid start_time: {}".format(start_time))
        else:
            start_time_ret = start_time
        if isinstance(end_time, str):
            end_time_ret = dateparser.parse(end_time, settings=TIMEZONE)  # type: ignore
            if end_time_ret is None:
                raise ValueError("Invalid end_time: {}".format(end_time))
        else:
            end_time_ret = end_time

        return start_time_ret, end_time_ret

    @staticmethod
    def _convert_to_bool_helper(x):
        if isinstance(x, bool):
            return x
        if x:
            return strtobool(str(x))
        return None

    def _prepare_pandas_dataframe(
        self,
        data: List[Dict[str, Any]],
        column: Optional[str] = None,
    ) -> pd.DataFrame:
        df = pd.DataFrame.from_records(data)
        if df.empty:
            return _build_empty_df_with_schema(self._dtypes)

        if column:
            if column not in df.columns:
                raise ValueError("Column {} not found in Gantry dataframe".format(column))

            df = (
                df[[DRUID_TIME_COLUMN_NAME, column]] if DRUID_TIME_COLUMN_NAME in df else df[column]
            )

        if isinstance(df, pd.Series):
            df = df.to_frame()

        if DRUID_TIME_COLUMN_NAME in df:
            df[DRUID_TIME_COLUMN_NAME] = pd.to_datetime(
                df[DRUID_TIME_COLUMN_NAME], unit="ms", utc=True
            )
            df = (
                df.rename(columns={DRUID_TIME_COLUMN_NAME: TIME_COLUMN_NAME})
                .set_index(TIME_COLUMN_NAME)
                .sort_index()
            )

        # Some Gantry types correspond directly to pd types; others will be parsed as objects.
        # Note that the timestamp, if applicable, is not a column, but rather the index itself.
        dtypes_property = self._dtypes  # _dtypes is a @property which makes a metadata API call.
        for col in df.columns:
            dtype = dtypes_property.get(col)

            # Bool columns from druid can be "true," "false," or None.
            # To convert to pandas boolean type we must first
            # convert to python bool where we can.
            if dtype == "bool":
                df[col] = df[col].map(self._convert_to_bool_helper).astype(pd.BooleanDtype())

            if dtype == "str":
                df[col] = df[col].astype(pd.StringDtype())

            if dtype == "category":
                df[col] = df[col].astype(pd.CategoricalDtype())

            if dtype == "float":
                df[col] = df[col].astype(float)

            if dtype == "int":
                # if null are present, will become float
                df[col] = df[col].astype(int, errors="ignore")

        return df[df.columns.sort_values(ascending=True)]

    def _head(
        self,
        n: int = 5,
        column: Optional[str] = None,
        query_filters: Optional[List[dict]] = None,
        tags: Optional[dict] = None,
    ) -> pd.DataFrame:
        """
        Return the first n rows.
        This function returns the first n rows for the object based
        on position. It is useful for quickly testing if your object
        has the right type of data in it.

        Note: This does not populate the dataframe's GantrySeries as this would be a subset
        of the frame's expected timeseries data.
        """
        if not (n > 0):
            raise ValueError("n must be a positive int. Got {}".format(n))
        data = self._populate_raw_request(
            query_filters=query_filters,
            ascending=True,
            n=n,
            tags=tags,
        )
        return self._prepare_pandas_dataframe(data, column)

    def _tail(
        self,
        n: int = 5,
        column: Optional[str] = None,
        query_filters: Optional[List[dict]] = None,
        tags: Optional[dict] = None,
    ) -> pd.DataFrame:
        """
        Return the last n rows.
        This function returns the last n rows for the object based
        on position. It is useful for quickly testing if your object
        has the right type of data in it.

        Note: This does not populate the dataframe's GantrySeries as this would be a subset
        of the frame's expected timeseries data.
        """
        if not (n > 0):
            raise ValueError("n must be a positive int. Got {}".format(n))
        data = self._populate_raw_request(
            query_filters=query_filters,
            ascending=False,
            n=n,
            tags=tags,
        )
        return self._prepare_pandas_dataframe(data, column)

    def _fetch(
        self,
        column: Optional[str] = None,
        query_filters: Optional[List[dict]] = None,
        tags: Optional[dict] = None,
    ) -> pd.DataFrame:
        """
        Return all data in the query window.
        """
        data = self._populate_raw_request(
            query_filters=query_filters,
            ascending=True,
            n=None,
            tags=tags,
        )
        return self._prepare_pandas_dataframe(data, column)

    def _populate_raw_request(
        self,
        n: Optional[int] = None,
        ascending: bool = True,
        query_filters: Optional[List[dict]] = None,
        tags: Optional[dict] = None,
    ):
        json_data: Dict[str, Any] = defaultdict(lambda: {})

        if tags:
            json_data["tags"] = tags

        if query_filters and len(query_filters) > 0:
            json_data["filters"] = query_filters

        if self.query_info.environment:
            json_data["tags"]["env"] = self.query_info.environment

        if n:
            json_data["limit"] = n
        else:
            json_data["limit"] = DEFAULT_FETCH_BATCH_SIZE

        json_data["order"] = ORDER_ASCENDING if ascending else ORDER_DESCENDING
        json_data["include_join_id"] = True

        events = []
        has_next = True
        while has_next:
            response = _get_raw_data(self.api_client, self.query_info, json.dumps(json_data))
            events.extend(response["events"])
            to_fetch = n or response["metadata"]["count"]
            has_next = response["metadata"]["has_next"] and (len(events) < to_fetch)
            json_data["offset"] = len(events)

        # Invert list if ascending is False because
        # the ORDER_DESCENDING parameter will return the
        # events in reverse order.
        data = events if ascending else events[::-1]

        # It's possible to retrieve more than the requested number of events
        # when n is large and doesn't fit in the first request.
        return data[:n] if n else data
