import functools
import warnings
from typing import Dict, List, Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

import pandas as pd

from gantry.query.core.dataframe import GantrySeries
from gantry.query.core.utils import same_size


def _prepare_pandas_dataframe(stat, results, dropna) -> pd.DataFrame:
    df = pd.DataFrame.from_records(results)
    if df.empty:
        return df

    # note that if num_points is 1, the timestamp is start_time
    # this is probably better than using end_time because
    # end_time is possibly in the future
    df.time_stamp = pd.to_datetime(df.time_stamp)
    df.rename(columns={"value": stat, "time_stamp": "timestamp"}, inplace=True)

    if dropna:
        df = df.dropna()

    return df.set_index("timestamp")


def categorical(func):
    @functools.wraps(func)
    def categorical_dec(self, outputs: GantrySeries, feedback: GantrySeries, *args, **kwargs):
        if outputs.datatype != "float":
            return func(self, outputs, feedback, *args, **kwargs)
        else:
            raise NotImplementedError()

    return categorical_dec


def regression(func):
    @functools.wraps(func)
    def regression_dec(self, outputs: GantrySeries, feedback: GantrySeries, *args, **kwargs):
        if outputs.datatype == "float":
            return func(self, outputs, feedback, *args, **kwargs)
        else:
            raise NotImplementedError()

    return regression_dec


def score(func):
    @functools.wraps(func)
    def score_dec(self, outputs: GantrySeries, feedback: GantrySeries, *args, **kwargs):
        if outputs.datatype == "float" and feedback.datatype != "float":
            return func(self, outputs, feedback, *args, **kwargs)
        else:
            raise NotImplementedError(
                "Outputs and feedback do not have the appropriate types to calculate score metrics"
            )

    return score_dec


def bool_type_check(func):
    @functools.wraps(func)
    def bool_dec(self, data_node: GantrySeries, *args, **kwargs):
        if data_node.datatype == "bool":
            return func(self, data_node, *args, **kwargs)
        else:
            raise NotImplementedError("Series type is not bool!")

    return bool_dec


def check_comparable(series_a, series_b):
    if not all(
        [filter_a == filter_b for filter_a, filter_b in zip(series_a.filters, series_b.filters)]
    ):
        raise ValueError(
            "Series A and series B do not have the same filters. "
            "Series A filters: {}\nSeries B filters: {}".format(series_a.filters, series_b.filters)
        )


class GantryMetric(object):
    """
    Gantry metric computations.

    Inspired by and references `sklearn metrics
    <https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics>`_

    For all queries, we use the first available GantrySeries's QueryInfo to obtain
    the relevant query metadata window.
    """

    def __init__(self, api_client) -> None:
        self._api_client = api_client

    def _metric_query(
        self,
        data_nodes: List[GantrySeries],
        stat: str,
        num_points: Optional[int] = None,
        stat_kwargs: Optional[dict] = None,
    ) -> List[Dict]:
        if (num_points is not None) and (num_points < 1):
            raise ValueError(
                "num_points must be greater than 0 if passed. Got {}.".format(num_points)
            )

        if not (1 <= len(data_nodes) <= 2):
            raise ValueError("Please provide 1 or 2 data_nodes in your query.")

        # TODO if data_nodes don't have the same parent dataframe
        # or have different query_info, we should raise an error. Can check filters.
        if len(data_nodes) == 2:
            check_comparable(data_nodes[0], data_nodes[1])

        data = {
            "start_time": data_nodes[0].query_info.start_time,
            "end_time": data_nodes[0].query_info.end_time,
            "num_points": num_points,
            "queries": {
                "query_label": {
                    "query_type": "data_node_ids",
                    "model_node_id": data_nodes[0].query_info.application_node_id,
                    "stat": stat,
                    "stat_kwargs": stat_kwargs or {},
                    "filters": data_nodes[0].filters,
                    "start_time": data_nodes[0].query_info.start_time,
                    "end_time": data_nodes[0].query_info.end_time,
                    "data_node_ids": [data_node.id for data_node in data_nodes],
                },
            },
        }

        response = self._api_client.request(
            "POST", "/api/v1/time_series/query", json=data, raise_for_status=True
        )
        return response["data"]["query_label"].get("points", [])

    @categorical
    @same_size("outputs", "feedback")
    def accuracy_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Categorical metric - accuracy

        In multilabel classification, this computes the set of |outputs| which exactly match
        the available |feedback|.

        Args:
            outputs (GantrySeries): predictions as a GantrySeries
            feedback (GantrySeries): labels to compare against as
                a GantrySeries
            dropna (bool, defaults to False): if True, drop rows with NaN
                values in result
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) accuracy score
        """
        stat = "accuracy_score"
        results = self._metric_query(
            [outputs, feedback],
            stat,
            num_points=num_points,
        )
        return _prepare_pandas_dataframe(stat, results, dropna=dropna)

    @regression
    @same_size("outputs", "feedback")
    def mean_squared_error(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        multioutput: Literal["uniform_average", "raw_values"] = "uniform_average",
        squared: bool = True,
    ) -> pd.DataFrame:
        """
        Regression metric- mean squared error

        Args:
            outputs (GantrySeries): predictions as a GantrySeries
            feedback (GantrySeries): labels to compare against as a GantrySeries
            dropna (bool, defaults to False): if True, drop rows with NaN values in result
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into.
            multioutput ("uniform_average" or "raw_values"): type of
                averaging to use when computing the metric. Defaults to
                "uniform_average".
            squared (boo, defaults to True): if True, return the squared error.

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) mean_squared_error
        """
        stat = "mean_squared_error"
        results = self._metric_query(
            [outputs, feedback],
            stat,
            num_points=num_points,
            stat_kwargs={"multioutput": multioutput, "squared": squared},
        )
        return _prepare_pandas_dataframe(stat, results, dropna=dropna)

    @categorical
    @same_size("outputs", "feedback")
    def confusion_matrix(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Categorical metric - confusion matrix
        The confusion matrix is a matrix :math:`C` where :math:`C_{i, j}`
        represents the number of times a data point from the class :math:`i`
        was predicted to be in class :math:`j`.

        Args:
            outputs (GantrySeries): predictions as a GantrySeries
            feedback (GantrySeries): labels to compare against as a
                GantrySeries.
            dropna (bool, defaults to False): if True, drop rows with NaN
                values in result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1)
                confusion_matrix
        """
        stat = "confusion_matrix"
        results = self._metric_query(
            [outputs, feedback],
            stat,
            num_points=num_points,
        )
        return _prepare_pandas_dataframe(stat, results, dropna=dropna)

    @categorical
    @same_size("outputs", "feedback")
    def f1_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        average: Literal["micro"] = "micro",
    ) -> pd.DataFrame:
        """
        Categorical metric - F1 score

        It is computed as the harmonic mean of precision and recall:
        F1 = 2 * (precision * recall) / (precision + recall)
        In multiclass classification, this is the average of the F1 score for all available classes.

        Args:
            outputs (GantrySeries): predictions as a GantrySeries
            feedback (GantrySeries): labels to compare against as a
                GantrySeries.
            dropna (bool, defaults to False): if True, drop rows with NaN
                values in result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into
            average ("micro"): type of averaging to use when computing
                the metric. Currently only "micro" supported, which is
                the default value.

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) f1_score
        """
        stat = "f1_score"
        results = self._metric_query(
            [outputs, feedback],
            stat,
            num_points=num_points,
            stat_kwargs={"average": average},
        )
        return _prepare_pandas_dataframe(stat, results, dropna=dropna)

    @regression
    @same_size("outputs", "feedback")
    def r2_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        multioutput: Literal[
            "uniform_average", "raw_values", "variance_weighted"
        ] = "uniform_average",
    ) -> float:
        """
        Regression metric- R^2 coefficient of determination

        Args:
            outputs (GantrySeries): predictions as a GantrySeries
            feedback (GantrySeries): labels to compare against as a
                GantrySeries.
            dropna (bool, defaults to False): if True, drop rows with NaN
                values in result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into
            multioutput ("uniform_average", "raw_values", "variance_weighted"):
                type of averaging to use when computing the metric. Defaults
                to "uniform_average".

        Returns:
            (float) R^2 score.
        """
        stat = "r2_score"
        results = self._metric_query(
            [outputs, feedback],
            stat,
            num_points=num_points,
            stat_kwargs={"multioutput": multioutput},
        )
        return _prepare_pandas_dataframe(stat, results, dropna=dropna)

    @categorical
    @same_size("outputs", "feedback")
    def precision_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        average: Literal["micro"] = "micro",
    ) -> pd.DataFrame:
        """
        Categorical metric - precision score

        precision =
        (number of true positives) / ((number of true positives) + (number of false positives))

        Args:
            outputs (GantrySeries): predictions as a GantrySeries
            feedback (GantrySeries): labels to compare against as a
                GantrySeries.
            dropna (bool, defaults to False): if True, drop rows with NaN
                values in result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into
            average ("micro"): type of averaging to use when computing
                the metric. Currently only "micro" supported, which is
                the default value.

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) precision_score
        """
        stat = "precision_score"
        results = self._metric_query(
            [outputs, feedback],
            stat,
            num_points=num_points,
            stat_kwargs={"average": average},
        )
        return _prepare_pandas_dataframe(stat, results, dropna=dropna)

    @categorical
    @same_size("outputs", "feedback")
    def recall_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        average: Literal["micro"] = "micro",
    ) -> pd.DataFrame:
        """
        Categorical metric - recall score

        recall =
        (number of true positives) / ((number of true positives) + (number of false negatives))

        Args:
            outputs (GantrySeries): predictions as a GantrySeries
            feedback (GantrySeries): labels to compare against as a
                GantrySeries.
            dropna (bool, defaults to False): if True, drop rows with NaN
                values in result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into
            average ("micro"): type of averaging to use when computing
                the metric. Currently only "micro" supported, which is
                the default value.

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) recall_score
        """
        stat = "recall_score"
        results = self._metric_query(
            [outputs, feedback],
            stat,
            num_points=num_points,
            stat_kwargs={"average": average},
        )
        return _prepare_pandas_dataframe(stat, results, dropna=dropna)

    @score
    @same_size("outputs", "feedback")
    def roc_auc_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Classification score metric - the area under the ROC curve

        Args:
            outputs (GantrySeries): predictions as a GantrySeries
            feedback (GantrySeries): labels to compare against as a
                GantrySeries.
            dropna (bool, defaults to False): if True, drop rows with NaN
                values in result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) roc_auc_score
        """
        stat = "roc_auc_score"
        results = self._metric_query(
            [outputs, feedback],
            stat,
            num_points=num_points,
        )
        return _prepare_pandas_dataframe(stat, results, dropna=dropna)

    def _percent_query(
        self,
        stat,
        data_node: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        if dropna:
            data_node = data_node[data_node.notna()]  # type: ignore

        results = self._metric_query(
            [data_node],
            stat,
            num_points=num_points,
        )
        return _prepare_pandas_dataframe(stat, results, dropna=False)

    def percent_null(
        self,
        data_node: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Percent null/NaN

        Args:
            data_node (GantrySeries): GantrySeries which will be calculated
            dropna (bool, defaults to False): if True, drop rows with NaN
                values in result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) percent_null
        """
        if dropna:
            warnings.warn(
                "'dropna' parameter is no longer valid in this "
                "query as it was a bug. Please remove it as it "
                "will be removed in future versions"
            )

        stat = "percent_null"
        return self._percent_query(stat, data_node, False, num_points)

    @bool_type_check
    def percent_true(
        self,
        data_node: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Percent true

        Args:
            data_node (GantrySeries): GantrySeries which will be calculated
            dropna (bool, defaults to False): if True, first drops NaN values
                before calculating result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) percent_true
        """
        stat = "percent_true"
        return self._percent_query(stat, data_node, dropna, num_points)

    @bool_type_check
    def percent_false(
        self,
        data_node: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Percent false

        Args:
            data_node (GantrySeries): GantrySeries which will be calculated
            dropna (bool, defaults to False): if True, first drops NaN values
                before calculating result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) percent_false
        """
        stat = "percent_false"
        return self._percent_query(stat, data_node, dropna, num_points)

    @bool_type_check
    def percent_true_not_null(
        self,
        data_node: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Percent true after excluding null values

        Args:
            data_node (GantrySeries): GantrySeries which will be calculated
            dropna (bool, defaults to False): if True, first drops NaN values
                before calculating result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) percent_true_not_null
        """
        stat = "percent_true_not_null"
        return self._percent_query(stat, data_node, dropna, num_points)

    @bool_type_check
    def percent_false_not_null(
        self,
        data_node: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Percent false after excluding null values

        Args:
            data_node (GantrySeries): GantrySeries which will be calculated
            dropna (bool, defaults to False): if True, first drops NaN values
                before calculating result.
            num_points (int, defaults to 1): number of points to divide the
                time window of the GantrySeries into

        Returns:
            (pd.DataFrame) pd.DataFrame of shape (num_points, 1) percent_false_not_null
        """
        stat = "percent_false_not_null"
        return self._percent_query(stat, data_node, dropna, num_points)
