from typing import Literal, Optional, TypedDict, Union, Dict, Any
from azure.identity._internal.msal_credentials import MsalCredential
import requests
import logging
from omnia_timeseries.helpers import retry
from omnia_timeseries.models import TimeseriesRequestFailedException
from importlib import metadata
import platform

logger = logging.getLogger(__name__)
version = metadata.version("omnia-timeseries-api")
system_version_string = f'({platform.system()}; Python {platform.version()})' if platform.system(
) else f'(Python {platform.version()})'


@retry(logger=logger)
def _request(
    request_type,
    url,
    headers,
    payload=None,
    params=None
) -> Dict[str, Any]:

    response = requests.request(
        request_type, url, headers=headers, json=payload, params=params)
    if not response.ok:
        raise TimeseriesRequestFailedException(response)
    json_obj = response.json()
    return json_obj


class HttpClient:
    def __init__(self, azure_credential: MsalCredential, resource_id: str):
        self._azure_credential = azure_credential
        self._resource_id = resource_id

    def request(
        self,
        request_type: Literal['get', 'put', 'post', 'patch', 'delete'],
        url: str,
        payload: Optional[Union[TypedDict, dict, list]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:

        access_token = self._azure_credential.get_token(
            f'{self._resource_id}/.default')  # handles caching and refreshing internally
        headers = {
            'Authorization': f'Bearer {access_token.token}',
            'Content-Type': 'application/json',
            'User-Agent': f'Omnia Timeseries SDK/{version} {system_version_string}'
        }
        return _request(request_type=request_type, url=url, headers=headers, payload=payload, params=params)
