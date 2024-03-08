from typing import Literal, Optional, Union, Dict, Any
from azure.identity._internal.msal_credentials import MsalCredential
import requests
import logging

from omnia_timeseries.helpers import retry
from omnia_timeseries.models import TimeseriesRequestFailedException
from importlib import metadata
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import platform

from msal_bearer.BearerAuth import BearerAuth, get_login_name

ContentType = Literal[
    "application/json", "application/protobuf", "application/x-google-protobuf"
]

RequestType = Literal["get", "put", "post", "patch", "delete"]

logger = logging.getLogger(__name__)
version = metadata.version("omnia_timeseries")
system_version_string = (
    f"({platform.system()}; Python {platform.version()})"
    if platform.system()
    else f"(Python {platform.version()})"
)

RequestsInstrumentor().instrument()


@retry(logger=logger)
def _request(
    request_type: RequestType,
    url: str,
    auth,
    headers: Dict[str, Any],
    payload: Optional[Union[dict, list]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Union[Dict[str, Any], bytes]:

    response = requests.request(
        request_type, url, auth=auth, headers=headers, json=payload, params=params
    )
    if not response.ok:
        raise TimeseriesRequestFailedException(response)
    if (
        headers is not None
        and "Accept" not in headers
        or headers["Accept"] == "application/json"
    ):
        return response.json()
    else:
        return response.content


class HttpClient:
    def __init__(
        self,
        resource_id,
        azure_credential: MsalCredential = None,
    ):
        if resource_id is None or not isinstance(resource_id, str):
            raise ValueError(
                "Input resource id must be a valid Azure application (client) id"
            )

        self._resource_id = resource_id
        self._azure_credential = azure_credential

    def request(
        self,
        request_type: RequestType,
        url: str,
        accept: ContentType = "application/json",
        payload: Optional[Union[dict, list]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:

        headers = {
            "Content-Type": "application/json",
            "Accept": accept,
            "User-Agent": f"Omnia Timeseries SDK/{version} {system_version_string}",
        }
        return _request(
            request_type=request_type,
            url=url,
            headers=headers,
            payload=payload,
            params=params,
            auth=self.get_auth(),
        )

    def get_auth(self) -> BearerAuth:
        """Get bearer token for authenticating. 
        Uses azure credential if provided. Else attempts to get access token for on-behalf-of user using msal

        Returns:
            BearerAuth: Bearer token to use for authenticating against api.
        """
        scopes = [f"{self._resource_id}/.default"]
        if self._azure_credential is not None:
            access_token = self._azure_credential.get_token(
                scopes[0]
            )  # handles caching and refreshing internally
            return BearerAuth(access_token.token)

        tenantID = "3aa4a235-b6e2-48d5-9195-7fcf05b459b0"  # Equinor tenant
        clientID = "98fe146b-2687-4db9-9c84-45f4cd9063af"  # IOC-monitoring-sdk
        scopes = [f"{self._resource_id}/user_impersonation"]
        return BearerAuth.get_auth(
            tenantID=tenantID,
            clientID=clientID,
            scopes=scopes,
            username=f"{get_login_name()}@equinor.com",
        )
