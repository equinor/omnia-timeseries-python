from typing import Literal, Optional, TypedDict, Union, Dict, Any
from azure.identity._internal.msal_credentials import MsalCredential
import requests
import logging
from azure.identity import ManagedIdentityCredential
import os


from omnia_timeseries.helpers import retry
from omnia_timeseries.models import TimeseriesRequestFailedException
from importlib import metadata
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import platform

ContentType = Literal["application/json",
                      "application/protobuf", "application/x-google-protobuf"]

RequestType = Literal['get', 'put', 'post', 'patch', 'delete']

CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
credential = ManagedIdentityCredential(client_id=CLIENT_ID)

logger = logging.getLogger(__name__)
version = metadata.version("omnia_timeseries")
system_version_string = f'({platform.system()}; Python {platform.version()})' if platform.system(
) else f'(Python {platform.version()})'

RequestsInstrumentor().instrument()

@retry(logger=logger)
def _request(
    request_type: RequestType,
    url: str,
    headers: Dict[str, Any],
    payload: Optional[Union[TypedDict, dict, list]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Union[Dict[str, Any], bytes]:

    response = requests.request(
        request_type, url, headers=headers, json=payload, params=params)
    if not response.ok:
        raise TimeseriesRequestFailedException(response)
    if not "Accept" in headers or headers["Accept"] == "application/json":
        return response.json()
    else:
        return response.content


# class AzureAuthenticator:
#     def __init__(self, azure_credential):
#         self._azure_credential = azure_credential

#     def get_token(self, resource_id: str) -> str:
#         auth_endpoint = (
#             "https://management.azure.com/.default"
#             if "azureml" in resource_id.lower()
#             else f"{resource_id}/.default"
#         )

#         token = self._azure_credential.get_token(auth_endpoint)
#         return token.token


# class HttpClient:
#     def __init__(self, azure_credential: MsalCredential, resource_id: str):
#         self._azure_credential = azure_credential
#         self._resource_id = resource_id

#     def request(
#         self,
#         request_type: RequestType,
#         url: str,
#         accept: ContentType = "application/json",
#         payload: Optional[Union[TypedDict, dict, list]] = None,
#         params: Optional[Dict[str, Any]] = None
#     ) -> Any:

#         access_token = self._azure_credential.get_token(
#             f'{self._resource_id}/.default'
#         )

#         headers = {
#             'Authorization': f'Bearer {access_token.token}',
#             'Content-Type': 'application/json',
#             'Accept': accept,
#             'User-Agent': f'Omnia Timeseries SDK/{version} {system_version_string}'
#         }

#         print(f"Access token: {access_token.token}")
#         return _request(request_type=request_type, url=url, headers=headers, payload=payload, params=params)


class AzureAuthenticator:
    def __init__(self, azure_credential):
        self._azure_credential = azure_credential

    def get_auth_endpoint(self, resource_id: str) -> str:
        return (
            "https://management.azure.com/.default"
            if "azureml" in resource_id.lower()
            else f"{resource_id}/.default"
        )

    def get_token(self, resource_id: str) -> str:
        auth_endpoint = self.get_auth_endpoint(resource_id)
        token = self._azure_credential.get_token(auth_endpoint)
        return token.token


class HttpClient:
    def __init__(self, azure_authenticator: AzureAuthenticator, resource_id: str):
        self._azure_authenticator = azure_authenticator
        self._resource_id = resource_id

    def request(
        self,
        request_type: str,
        url: str,
        accept: str = "application/json",
        payload: Optional[Union[dict, list]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        
        # Get the auth endpoint from AzureAuthenticator
        auth_endpoint = self._azure_authenticator.get_auth_endpoint(self._resource_id)

        # Get the token for the resolved endpoint
        access_token = self._azure_authenticator.get_token(self._resource_id)


        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": accept,
            'User-Agent': f'Omnia Timeseries SDK/{version} {system_version_string}'
        }

        print(f"Using Auth Endpoint: {auth_endpoint}")
        print(f"Access Token: {access_token}")

        return self._request(request_type=request_type, url=url, headers=headers, payload=payload, params=params)