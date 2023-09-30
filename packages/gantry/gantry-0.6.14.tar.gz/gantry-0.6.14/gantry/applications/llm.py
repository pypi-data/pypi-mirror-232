import atexit
import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue
from typing import Callable, Dict, List, Optional, Union

import backoff
import requests

from gantry.const import PROD_API_URL
from gantry.exceptions import GantryRequestException

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

from gantry.api_client import APIClient
from gantry.applications.core import Application
from gantry.applications.llm_utils import _get_prompt_inputs
from gantry.applications.utils import get_models_to_vendor
from gantry.logger.consumer import BatchConsumer
from gantry.logger.stores import (
    BACKOFF_INTERVAL_FOR_ERROR_CODE_SECS,
    BACKOFF_INTERVAL_FOR_TIMEOUT_SECS,
    BATCH_UPLOAD_MAX_TRIES,
    BaseLogStore,
    backoff_giveup_handler,
    backoff_retry_handler,
    non_retry_error,
)

logger = logging.getLogger(__name__)

OPENAI_CHAT_VENDOR = "openai-chat"


@dataclass(frozen=True)
class VersionDetails:
    """
    A dataclass representing the details of a version.

    Attributes:
        config: (dict): Dictionary of key and value pairs that specify the data stored in the
            version.
        description: (str): Description of the version.
        app_name: (str): Name of the application.
        version_id: (uuid.UUID): UUID of the version.
        version_number: (int): Version number of the version.
    """

    config: dict
    description: str
    app_name: str
    version_id: uuid.UUID
    version_number: int


class LLMAPILogStore(ABC, BaseLogStore):
    """Log store implementation for LLM apps.

    Only streaming logging is supported. This implementation
    uses the completion logging endpoint for ingestion and does
    not perform data validation.

    """

    def __init__(
        self,
        api_client,
        consumer_factory=BatchConsumer,
    ):
        self._api_client = api_client

        self.num_consumer_threads: int = 1
        self.queue: Queue = Queue()

        self.consumers = []
        self._consumer_factory = consumer_factory
        # On program exit, allow the consumer thread to exit cleanly.
        # This prevents exceptions and a messy shutdown when the
        # interpreter is destroyed before the daemon thread finishes
        # execution.
        atexit.register(self._join)
        for _ in range(self.num_consumer_threads):
            consumer = self._consumer_factory(self.queue, self.consumer_func)
            self.consumers.append(consumer)
            consumer.start()

    @classmethod
    @abstractmethod
    def get_ingestion_endpoint(cls, vendor: str) -> str:
        pass

    def log(self, application: str, event: dict) -> None:
        """
        Logs a prediction or feedback event.

        Args:
            application: Name of the application
            event: Data to logs as event body
        """
        self.queue.put(event)

    def log_batch(self, application: str, events: List[dict]) -> None:
        raise NotImplementedError("Completion logging does not support batch.")

    def consumer_func(self, batch):
        # Catch all errors and do not raise in order
        # for thread consumer to continue running.
        try:
            for event in batch:
                self.send_completion_event(json.loads(event))
        except Exception as e:
            logger.error("Internal error sending events: %s", e)

    @backoff.on_exception(
        backoff.constant,
        (requests.Timeout, requests.ConnectionError),
        interval=BACKOFF_INTERVAL_FOR_TIMEOUT_SECS,
        max_tries=BATCH_UPLOAD_MAX_TRIES,
        on_backoff=backoff_retry_handler,
        on_giveup=backoff_giveup_handler,
        jitter=None,
    )
    @backoff.on_exception(
        backoff.constant,
        GantryRequestException,
        max_tries=BATCH_UPLOAD_MAX_TRIES,
        interval=BACKOFF_INTERVAL_FOR_ERROR_CODE_SECS,
        on_backoff=backoff_retry_handler,
        on_giveup=backoff_giveup_handler,
        giveup=non_retry_error,
        jitter=None,
    )
    def send_completion_event(self, event: Dict) -> None:
        # Use vendor to determine endpoint
        vendor = event.pop("vendor", "openai")

        response = self._api_client.request(
            "POST",
            self.get_ingestion_endpoint(vendor),
            json=event,
            raise_for_status=True,
        )
        if response.get("response") != "ok":
            logger.error("Failed to log events. Response = %s", response)

    def _join(self):
        for consumer in self.consumers:
            consumer.pause()
            try:
                consumer.join()
            except RuntimeError:
                # consumer thread has not started
                pass


class CompletionAPILogStore(LLMAPILogStore):
    @classmethod
    def get_ingestion_endpoint(cls, vendor: str) -> str:
        return f"/api/v1/logging/{vendor}/completions"


class ChatAPILogStore(LLMAPILogStore):
    @classmethod
    def get_ingestion_endpoint(cls, vendor: str) -> str:
        return "/api/v1/logging/chat/completions"


class CompletionApplication(Application):
    """
    A class representing a completion application, a subclass of Application. This has
    special logging methods for logging completions.
    """

    def __init__(
        self,
        name: str,
        api_client: APIClient,
        id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
        log_store_factory: Callable[[APIClient], BaseLogStore] = CompletionAPILogStore,
    ):
        super().__init__(name, api_client, id, organization_id)
        self._configuration_name = f"default_{name}_configuration"
        # TODO: validate name

        self._log_store = log_store_factory(api_client)

    def create_version(
        self,
        prompt_template: str,
        description: str,
        model: str,
        model_params: Optional[dict] = None,
        prompt_inputs: Optional[List[str]] = None,
    ) -> VersionDetails:
        """
        Creates a new version of a prompt template associated to this application.

        Example usage for a version using OpenAI Completion model:

        .. code-block:: python

            import gantry

            my_llm_app = gantry.get_application("my_llm_app")

            my_llm_app.create_version(
                prompt_template="This is a prompt template. {{input1}} {{input2}}",
                description="My first version",
                model="text-davinci-001",
                model_params={"temperature": 0.5},
                prompt_inputs=["input1", "input2"],
            )

        Example usage for a version using OpenAI Chat model with function support:

        .. code-block:: python

            import gantry

            my_llm_app = gantry.get_application("my_llm_app")

            my_llm_app.create_version(
                prompt_template=(
                    "Assistant: you are a helpful assistant\\n\\n"
                    "User: What's the weather in Boston?"
                ),
                description="My first version",
                model="gpt-4",
                model_params={
                    "temperature": 1,
                    "function_call": "auto",
                    "functions": [
                        {
                            "name": "get_current_weather",
                            "description": "Get the current weather in a given location",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "The city and state, e.g. San Francisco, CA"
                                    },
                                    "unit": {
                                        "type": "string",
                                        "enum": ["celsius", "fahrenheit"]
                                    }
                                },
                                "required": ["location"]
                            }
                        }
                    ]
                }
            )

        Example usage for a version using Cohere model:

        .. code-block:: python

            import gantry

            my_llm_app = gantry.get_application("my_llm_app")

            my_llm_app.create_version(
                prompt_template="This is a prompt template. {{input1}} {{input2}}",
                description="My first version",
                model="command",
                model_params={"max_tokens": 500},
                prompt_inputs=["input1", "input2"],
            )


        Example output:

        .. code-block:: python

            VersionDetails(
                config={
                    "model": "text-davinci-002",
                    "params": {
                        "frequency_penalty": 0.0,
                        "max_tokens": 16,
                        "presence_penalty": 0.0,
                        "temperature": 0.5,
                        "top_p": 1.0
                    },
                    "prompt": "This is a prompt template. {{input1}} {{input2}}",
                    "prompt_inputs": ["input1", "input2"],
                },
                description="My first version",
                app_name="my_llm_app",
                version_id=UUID("a1b2c3d4-e5f6-4a3b-8c2d-1e2f3a4b5c6d"),
                version_number=1,
            )


        IMPORTANT: 'functions' and 'function_call' are valid model_params only
            for 'openai-chat' vendor.

        Args:
            prompt_template (str): The prompt template to use for this version. Denote variables
                like this: `{{variable}}`
            description (str): A description of this version.
            model (str): The model to use for this version. Must be a valid OpenAI
                completion text model.
            model_params (dict, optional): A dictionary of model parameters to use for this prompt.
                See vendor's documentation for more details.
            prompt_inputs (List[str], optional): A list of input names to use for this prompt,
                when using prompt variables. If not provided, the function will attempt to extract
                the input names from the prompt template.

        Returns:
            VersionDetails: A dataclass containing the configuration data, description, application
            name, version ID, and version number of the newly created version.
        """
        models_to_vendor = get_models_to_vendor(self._api_client)

        if model not in models_to_vendor:
            raise ValueError(
                f"Model '{model}' not supported. Available models: {list(models_to_vendor.keys())}"
            )

        vendor = models_to_vendor[model]
        params = model_params or {}
        if "functions" in params.keys() or "function_call" in params.keys():
            if vendor != OPENAI_CHAT_VENDOR:
                raise ValueError(
                    "'functions' and/or 'function_call' in model parameters "
                    "is only available for openai chat models."
                )

        configuration_data = {
            "prompt": prompt_template,
            "prompt_inputs": prompt_inputs or _get_prompt_inputs(prompt_template),
            "model": model,
            "params": params,
            "vendor": vendor,
        }

        res = self._api_client.request(
            "POST",
            f"/api/v1/cms/{self._name}/configurations/{self._configuration_name}/versions",
            json={
                "configuration_data": configuration_data,
                "description": description,
            },
            raise_for_status=True,
        )
        logger.info(
            "Version %s created for application '%s'",
            res["data"]["version"],
            self._name,
        )
        host = os.environ.get("GANTRY_LOGS_LOCATION", PROD_API_URL)
        link_to_versions = "{}/applications/{}/versions/".format(host, self._name)
        logger.info("See the new version here: %s", link_to_versions)

        return VersionDetails(
            config=configuration_data,
            description=description,
            app_name=self._name,
            version_id=uuid.UUID(res["data"]["id"]),
            version_number=res["data"]["version"],
        )

    def get_version(self, version: Literal["prod", "test", "latest"]) -> Optional[VersionDetails]:
        """
        Returns the prompt configuration data for a given version of this application.

        Example usage:

        .. code-block:: python

            import gantry

            my_llm_app = gantry.get_application("my_llm_app")

            my_llm_app.get_version("prod")

        Example output:

        .. code-block:: python

            VersionDetails(
                config={
                    "model": "text-davinci-002",
                    "params": {
                        "frequency_penalty": 0.0,
                        "max_tokens": 16,
                        "presence_penalty": 0.0,
                        "temperature": 0.5,
                        "top_p": 1.0
                    },
                    "prompt": "This is a prompt template. {{input1}} {{input2}}",
                    "prompt_inputs": ["input1", "input2"],
                },
                description="My first version",
                app_name="my_llm_app",
                version_id=UUID("a1b2c3d4-e5f6-4a3b-8c2d-1e2f3a4b5c6d"),
                version_number=1,
            )

        Args:
            version (Literal["prod", "test", "latest"]): The version to get. Can be one of "prod",
                "test", or "latest". When "latest" is used, the latest version will be returned,
                regardless of deployment status. When "prod" or "test" is used, the latest version
                that has been deployed to that environment will be returned.

        Returns:
            Optional[VersionDetails]: A dataclass containing the configuration data, description,
            application name, version ID, and version number of the requested version. If no
            version is found, returns None.
        """
        version_data: dict

        try:
            if version == "latest":
                # for latest version, we get a list of all versions and pick the most recent
                res = self._api_client.request(
                    "GET",
                    f"/api/v1/cms/{self._name}/configurations/{self._configuration_name}/versions",
                    raise_for_status=True,
                )
                version_data = res["data"][0]
            elif version in ["prod", "test"]:
                # for releases, we can get the latest release by environment
                res = self._api_client.request(
                    "GET",
                    f"/api/v1/cms/{self._name}/configurations/{self._configuration_name}/releases",
                    params={"latest": True, "env": version},
                    raise_for_status=True,
                )
                version_data = res["data"][0]["version"]
            else:
                raise ValueError(
                    f"Invalid version '{version}'. Must be one of 'prod', 'test', or 'latest'"
                )
        except IndexError:
            logger.warn("No version found for '%s'", version)
            return None

        # now that we have the version, we can get the config data
        res = self._api_client.request(
            "GET",
            (
                f"/api/v1/cms/{self._name}/configurations/{self._configuration_name}"
                f"/versions/{version_data['id']}/data"
            ),
            raise_for_status=True,
        )
        config_data = res["data"][0]

        return VersionDetails(
            config=config_data,
            description=version_data["description"],
            app_name=self._name,
            version_id=uuid.UUID(version_data["id"]),
            version_number=version_data["version"],
        )

    def log_llm_data(
        self,
        api_request: Dict,
        api_response: Dict,
        request_attributes: Optional[Dict] = None,
        response_attributes: Optional[Dict] = None,
        feedback: Optional[Dict] = None,
        selected_choice_index: int = 0,
        session_id: Optional[Union[str, uuid.UUID]] = None,
        tags: Optional[Dict] = None,
        version: Optional[int] = None,
        vendor: str = "openai",
    ):
        """
        Log request/response LLM completion pair into Gantry
        from several vendors. See documentation on supported
        vendors.

        Example usage:

        .. code-block:: python

            import gantry
            from gantry.applications.llm_utils import fill_prompt
            import openai
            from openai.util import convert_to_dict

            gantry.init()
            my_llm_app = gantry.get_application("my-llm-app")

            version = my_llm_app.get_version("test")
            # "latest", "prod", or "test"
            config = version.config
            prompt = config['prompt']

            def generate(values):
                filled_in_prompt = fill_prompt(prompt, values)
                request = {
                    "model": "text-davinci-002",
                    "prompt": filled_in_prompt,
                }
                results = openai.Completion.create(**request)

                my_llm_app.log_llm_data(
                    api_request=request,
                    api_response=convert_to_dict(results),
                    request_attributes={"prompt_values": values},
                    version=version.version_number,
                )

                return results

        Args:
            api_request (dict): The LLM completion request.
            response (dict): The LLM completion response.
            request_attributes (Optional[dict]): Additional inputs
            response_attributes (Optional[dict]): Additional outputs
            feedback (Optional[dict]): Optional feedback data. See
                https://docs.gantry.io/docs/logging-feedback-actuals for more information
                about logging feedback in Gantry.
            selected_choice_index (Optional[int]): The selected choice index. Defaults to 1.
            session_id (Optional[str or uuid.UUID]): Optional session
                to group data together.
            tags (Optional[dict]): Optional tags to add to the record.
            version (Optional[int]): The version number used.
            vendor (str, defaults to 'openai'): The vendor the data
                is from. See Gantry documentation for supported vendors.
        """
        tags = tags or {}
        if version:
            tags["version_number"] = version

        event = {
            "application": self._name,
            "api_request": api_request,
            "api_response": api_response,
            "request_attributes": request_attributes or {},
            "response_attributes": response_attributes or {},
            "feedback": feedback or {},
            "selected_choice_index": selected_choice_index,
            "session_id": session_id,
            "tags": tags,
            "vendor": vendor,
        }

        self._log_store.log(self._name, event)

    def deploy_version(self, version_id: uuid.UUID, env: Literal["prod", "test"]) -> None:
        """
        Deploys a version in a specific environment.

        Example usage:

        .. code-block:: python

            import gantry

            my_llm_app = gantry.get_application("my_llm_app")
            version = my_llm_app.get_version("latest")
            my_llm_app.deploy_version(version.version_id, "prod")

        Args:
            version_id (uuid): The version id.
            env (str, 'prod' or 'test'): The target environment, can be 'prod' or 'test'.

        """
        _ = self._api_client.request(
            "PATCH",
            (f"/api/v1/cms/{self._name}/configurations/{self._configuration_name}" "/releases"),
            json={
                "version_id": str(version_id),
                "env": env,
                "description": "Deployment from SDK",
            },
            raise_for_status=True,
        )
        logger.info(f"Version {version_id} was successfully deployed in {env}")


class ChatApplication(Application):
    """
    A class representing a chat application, a subclass of Application. This has
    special logging methods for logging chat completions.
    """

    def __init__(
        self,
        name: str,
        api_client: APIClient,
        id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
        log_store_factory: Callable[[APIClient], BaseLogStore] = ChatAPILogStore,
    ):
        super().__init__(name, api_client, id, organization_id)
        self._configuration_name = f"default_{name}_configuration"
        # TODO: validate name

        self._log_store = log_store_factory(api_client)

    def create_version(
        self,
        prompt_template: str,
        description: str,
        model: str,
        model_params: Optional[dict] = None,
        prompt_inputs: Optional[List[str]] = None,
    ) -> VersionDetails:
        """
        Creates a new version of a prompt template associated to this application.

        Example usage for a version using OpenAI Chat model:

        .. code-block:: python

            import gantry

            my_llm_app = gantry.get_application("my_llm_app")

            my_llm_app.create_version(
                prompt_template="This is a prompt template. {{input1}} {{input2}}",
                description="My first version",
                model="gpt-4",
                model_params={"temperature": 0.5},
                prompt_inputs=["input1", "input2"],
            )

        Example usage for a version using OpenAI Chat model with function support:

        .. code-block:: python

            import gantry

            my_llm_app = gantry.get_application("my_llm_app")

            my_llm_app.create_version(
                prompt_template=(
                    "Assistant: you are a helpful assistant\\n\\n"
                    "User: What's the weather in Boston?"
                ),
                description="My first version",
                model="gpt-4",
                model_params={
                    "temperature": 1,
                    "function_call": "auto",
                    "functions": [
                        {
                            "name": "get_current_weather",
                            "description": "Get the current weather in a given location",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "The city and state, e.g. San Francisco, CA"
                                    },
                                    "unit": {
                                        "type": "string",
                                        "enum": ["celsius", "fahrenheit"]
                                    }
                                },
                                "required": ["location"]
                            }
                        }
                    ]
                }
            )

        Example output:

        .. code-block:: python

            VersionDetails(
                config={
                    "model": "gpt-4",
                    "params": {
                        "frequency_penalty": 0.0,
                        "max_tokens": 16,
                        "presence_penalty": 0.0,
                        "temperature": 0.5,
                        "top_p": 1.0
                    },
                    "prompt": "This is a prompt template. {{input1}} {{input2}}",
                    "prompt_inputs": ["input1", "input2"],
                },
                description="My first version",
                app_name="my_llm_app",
                version_id=UUID("a1b2c3d4-e5f6-4a3b-8c2d-1e2f3a4b5c6d"),
                version_number=1,
            )



        Args:
            prompt_template (str): The prompt template to use for this version. Denote variables
                like this: `{{variable}}`
            description (str): A description of this version.
            model (str): The OpenAI model to use for this version. Must be a valid OpenAI
                completion text model.
            model_params (dict, optional): A dictionary of model parameters to use for this prompt.
                Valid keys are: temperature, max_tokens, top_p, frequency_penalty, presence_penalty.
                See OpenAI's documentation for more details.
            prompt_inputs (List[str], optional): A list of input names to use for this prompt,
                when using prompt variables. If not provided, the function will attempt to extract
                the input names from the prompt template.

        Returns:
            VersionDetails: A dataclass containing the configuration data, description, application
            name, version ID, and version number of the newly created version.
        """
        params = model_params or {}

        configuration_data = {
            "prompt": prompt_template,
            "prompt_inputs": prompt_inputs or _get_prompt_inputs(prompt_template),
            "model": model,
            "params": params,
            "vendor": "openai-chat",
        }

        res = self._api_client.request(
            "POST",
            f"/api/v1/cms/{self._name}/configurations/{self._configuration_name}/versions",
            json={
                "configuration_data": configuration_data,
                "description": description,
            },
            raise_for_status=True,
        )
        logger.info(
            "Version %s created for application '%s'",
            res["data"]["version"],
            self._name,
        )
        host = os.environ.get("GANTRY_LOGS_LOCATION", PROD_API_URL)
        link_to_versions = "{}/applications/{}/versions/".format(host, self._name)
        logger.info("See the new version here: %s", link_to_versions)

        return VersionDetails(
            config=configuration_data,
            description=description,
            app_name=self._name,
            version_id=uuid.UUID(res["data"]["id"]),
            version_number=res["data"]["version"],
        )

    def log_llm_data(
        self,
        api_request: Dict,
        api_response: Dict,
        request_attributes: Optional[Dict] = None,
        response_attributes: Optional[Dict] = None,
        feedback: Optional[Dict] = None,
        selected_choice_index: int = 0,
        session_id: Optional[Union[str, uuid.UUID]] = None,
        tags: Optional[Dict] = None,
        version: Optional[int] = None,
    ):
        """
        Log request/response OpenAI chat pair into Gantry.

        Example usage:

        .. code-block:: python

            import gantry
            from gantry.applications.llm_utils import fill_prompt
            import openai
            from openai.util import convert_to_dict

            gantry.init()
            my_llm_app = gantry.get_application("my-llm-app")

            version = my_llm_app.get_version("test")
            # "latest", "prod", or "test"
            config = version.config
            prompt = config['prompt']

            def generate(values):
                filled_in_prompt = fill_prompt(prompt, values)
                request = {
                    "model": "text-davinci-002",
                    "prompt": filled_in_prompt,
                }
                results = openai.Completion.create(**request)

                my_llm_app.log_llm_data(
                    api_request=request,
                    api_response=convert_to_dict(results),
                    request_attributes={"prompt_values": values},
                    version=version.version_number,
                )

                return results

        For more details on request/response content, see `OpenAI API Reference for Completion
        <https://platform.openai.com/docs/api-reference/completions/create>`_.

        Args:
            api_request (dict): The OpenAI request.
                For more details on content, see `OpenAI API Reference for Completion
                <https://platform.openai.com/docs/api-reference/completions/create>`_.
            api_response (dict): The OpenAI response.
                For more details on content, see `OpenAI API Reference for Completion
                <https://platform.openai.com/docs/api-reference/completions/create>`_.
            request_attributes (Optional[dict]): Additional inputs
            response_attributes (Optional[dict]): Additional outputs
            feedback (Optional[dict]): Optional feedback data. See
                https://docs.gantry.io/docs/logging-feedback-actuals for more information
                about logging feedback in Gantry.
            selected_choice_index (Optional[int]): The selected choice index. Defaults to 1.
            session_id (Optional[str or uuid.UUID]): Optional session
                to group data together.
            tags (Optional[dict]): Optional tags to add to the record.
            version (Optional[int]): The version number used.
        """
        tags = tags or {}
        if version:
            tags["version_number"] = version

        event = {
            "application": self._name,
            "api_request": api_request,
            "api_response": api_response,
            "request_attributes": request_attributes or {},
            "response_attributes": response_attributes or {},
            "feedback": feedback or {},
            "selected_choice_index": selected_choice_index,
            "session_id": session_id,
            "tags": tags,
        }

        self._log_store.log(self._name, event)
