from typing import Literal, Optional, TypedDict, Union, Dict, Any
from azure.identity._internal.msal_credentials import MsalCredential
import requests
import logging
from omnia_timeseries.helpers import retry
from requests.models import Response
import json

logger = logging.getLogger(__name__)

class TimeseriesRequestFailedException(Exception):
    def __init__(self, response:Response) -> None:
        error = json.loads(response.text)
        self._status_code = response.status_code
        self._reason = response.reason
        self._message = error["message"]
        self._trace_id = error["traceId"]
        super().__init__(f"Status code: {self._status_code}, Reason: {self._reason}, Message: {self._message},  Trace ID: {self._trace_id}")

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def reason(self) -> str:
        return self._reason

    @property
    def message(self) -> str:
        return self._message

    @property
    def trace_id(self) -> str:
        return self._trace_id

@retry(logger=logger)
def _request(
        request_type, 
        url, 
        headers, 
        payload=None,
        params=None
    ) -> Dict[str, Any]:

    response = requests.request(request_type, url, headers=headers, json=payload, params=params)
    if not response.ok:
        raise TimeseriesRequestFailedException(response)
    json_obj = response.json()
    return json_obj

class HttpClient:
    def __init__(self, azure_credential:MsalCredential, resource_id:str):
        self._azure_credential = azure_credential
        self._resource_id = resource_id

    def request(
            self, 
            request_type:Literal['get', 'put', 'post', 'patch', 'delete'], 
            url:str, 
            payload:Optional[Union[TypedDict, dict, list]]=None,
            params:Optional[Dict[str, Any]]=None
        ) -> Any:

        access_token = self._azure_credential.get_token(f'{self._resource_id}/.default') # handles caching and refreshing internally
        headers = {
            'Authorization': f'Bearer {access_token.token}',
            'Content-Type': 'application/json'
        }
        return _request(request_type=request_type, url=url, headers=headers, payload=payload, params=params)
