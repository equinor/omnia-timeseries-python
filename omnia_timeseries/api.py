from typing import List, Literal, Optional
from azure.identity._internal.msal_credentials import MsalCredential
from omnia_timeseries.http_client import HttpClient
from omnia_timeseries.models import (
    DatapointModel, 
    DatapointsItemsModel, DatapointsPostRequestModel,
    FacilityDataModel, GetAggregatesResponseModel, GetDatapointsResponseModel, GetHistoryResponseModel, GetMultipleDatapointsRequestItem, GetTimeseriesResponseModel, 
    MessageModel, 
    StreamSubscriptionRequestModel, 
    StreamSubscriptionDataModel,
    TimeseriesPatchRequestItem, TimeseriesRequestItem
)
import logging

logger = logging.getLogger(__name__)

class TimeseriesEnvironment:
    def __init__(self, resource_id:str, base_url:str):
        self._resource_id = resource_id
        self._base_url = base_url

    @classmethod
    def Beta(cls):
        return cls(
            resource_id="32f2a909-8a98-4eb8-b22d-1208d9350cb0", 
            base_url="https://api.gateway.equinor.com/plant-beta/timeseries/v1.6"
        )

    @classmethod
    def Prod(cls):
        return cls(
            resource_id="141369bd-3dca-4b55-825b-56ad4a69b1fc", 
            base_url="https://api.gateway.equinor.com/plant/timeseries/v1.6"
        )

    @property
    def resource_id(self) -> str:
        return self._resource_id

    @property
    def base_url(self) -> str:
        return self._base_url

class TimeseriesAPI:
    """
    Wrapper class for interacting with the Omnia Industrial IIoT Timeseries API.
    For more information, see https://github.com/equinor/OmniaPlant/wiki or consult with the Omnia IIoT team.
    Args:
        :param azure_credential: Azure credential instance used for authenticating
        :type azure_credential: MsalCredential

        :param environment: API deployment environment
        :type environment: TimeseriesEnvironment
    """
    def __init__(self, azure_credential:MsalCredential, environment:TimeseriesEnvironment):
        self._http_client = HttpClient(azure_credential=azure_credential, resource_id=environment.resource_id)
        self._base_url = environment.base_url.rstrip('/')

    def write_data(self, id:str, data:DatapointsPostRequestModel, is_async:Optional[bool]=None) -> MessageModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/writeData"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/{id}/data",
            params={'async': is_async} if is_async is not None else None,
            payload=data
        )

    def write_multiple(self, items:DatapointsItemsModel, is_async:Optional[bool]=None) -> MessageModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/writeMultipleData"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/data",
            params={'async': is_async} if is_async is not None else None,
            payload=items
        )

    def get_datapoints(
        self,
        id: str,
        startTime: Optional[str]=None,
        endTime: Optional[str]=None,
        status: Optional[List[int]]=None,
        includeOutsidePoints: Optional[bool]=None,
        limit: Optional[int]=None,
        continuationToken: Optional[str]=None) -> GetDatapointsResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getDatapoints"""
        params = {}
        if startTime is not None:
            params['startTime'] = startTime
        if endTime is not None:
            params['endTime'] = endTime
        if status is not None:
            params['status'] = status
        if includeOutsidePoints is not None:
            params['includeOutsidePoints'] = includeOutsidePoints
        if limit is not None:
            params['limit'] = limit
        if continuationToken is not None:
            params['continuationToken'] = continuationToken
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/data",
            params=params
        )

    def get_multi_datapoints(self, request: List[GetMultipleDatapointsRequestItem]) -> GetAggregatesResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getMultiDatapoints"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/query/data",
            payload=request
        )

    def get_aggregates(
        self,
        id: str,
        aggregateFunction: List[Literal['avg', 'min', 'max', 'sum', 'stddev', 'count', 'first', 'last']],
        startTime: Optional[str]=None,
        endTime: Optional[str]=None,
        status: Optional[List[int]]=None,
        processingInterval: Optional[str]=None,
        fill: Optional[str]=None,
        limit: Optional[int]=None,
        continuationToken: Optional[str]=None) -> GetAggregatesResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/get-aggregates"""
        params = {}
        if aggregateFunction is not None:
            params['aggregateFunction'] = aggregateFunction
        if startTime is not None:
            params['startTime'] = startTime
        if endTime is not None:
            params['endTime'] = endTime
        if status is not None:
            params['status'] = status
        if processingInterval is not None:
            params['processingInterval'] = processingInterval
        if fill is not None:
            params['fill'] = fill
        if limit is not None:
            params['limit'] = limit
        if continuationToken is not None:
            params['continuationToken'] = continuationToken
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/data/aggregates",
            params=params
        )

    def get_first_datapoint(self, id:str, afterTime:Optional[str]=None, beforeTime:Optional[str]=None, status:Optional[List[int]]=None) -> DatapointModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getFirstDatapoint"""
        params = {}
        if afterTime is not None:
            params['afterTime'] = afterTime
        if beforeTime is not None:
            params['beforeTime'] = beforeTime
        if status is not None:
            params['status'] = status
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/data/first",
            params=params
        )

    def get_latest_datapoint(self, id:str, afterTime:Optional[str]=None, beforeTime:Optional[str]=None, status:Optional[List[int]]=None) -> GetDatapointsResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getLatestDatapoint"""
        params = {}
        if afterTime is not None:
            params['afterTime'] = afterTime
        if beforeTime is not None:
            params['beforeTime'] = beforeTime
        if status is not None:
            params['status'] = status
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/data/latest",
            params=params
        )

    def get_first_multi_datapoint(self, request:List[GetMultipleDatapointsRequestItem]) -> GetDatapointsResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getFirstMultiDatapoint"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/query/data/first",
            payload=request
        )

    def get_latest_multi_datapoint(self, request:List[GetMultipleDatapointsRequestItem]) -> GetDatapointsResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getLastMultiDatapoint"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/query/data/latest",
            payload=request
        )

    def get_history(self, id:str) -> GetHistoryResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getHistory"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/history"
        )

    def get_timeseries(
        self, 
        name: Optional[str]=None, 
        externalId: Optional[str]=None,
        source: Optional[str]=None,
        assetId: Optional[str]=None,
        facility: Optional[str]=None,
        limit: Optional[int]=None,
        continuationToken: Optional[str]=None) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getTimeseries"""
        params = {}
        if name is not None:
            params['name'] = name
        if externalId is not None:
            params['externalId'] = externalId
        if source is not None:
            params['source'] = source
        if assetId is not None:
            params['assetId'] = assetId
        if facility is not None:
            params['facility'] = facility
        if limit is not None:
            params['limit'] = limit
        if continuationToken is not None:
            params['continuationToken'] = continuationToken
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}",
            params=params
        )

    def search_timeseries(
        self, 
        query: Optional[str]=None,
        name: Optional[str]=None,
        description: Optional[str]=None,
        unit: Optional[str]=None,
        continuationToken: Optional[str]=None) -> GetTimeseriesResponseModel:
        """
        Without query: https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getSearchWitoutQuery
        With query: https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getSearch
        """
        params = {}
        if name is not None:
            params['name'] = name
        if description is not None:
            params['description'] = description
        if unit is not None:
            params['unit'] = unit
        if continuationToken is not None:
            params['continuationToken'] = continuationToken
        url = f"{self._base_url}/search" if query is None else f"{self._base_url}/search/{query}"
        return self._http_client.request(
            request_type='get',
            url=url,
            params=params
        )

    def get_timeseries_by_id(self, id:str) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getTimeseriesById"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}"
        )

    def post_timeseries(self, request:TimeseriesRequestItem) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/postTimeseries"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}",
            payload=request
        )

    def get_or_add_timeseries(self, request:List[TimeseriesRequestItem]) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/postGetOrAddTimeseries"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/getoradd",
            payload=request
        )

    def patch_timeseries(self, id:str, request:TimeseriesPatchRequestItem) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/patchTimeseries"""
        return self._http_client.request(
            request_type='patch',
            url=f"{self._base_url}/{id}",
            payload=request
        )

    def put_timeseries(self, id:str, request:TimeseriesRequestItem) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/patchTimeseries"""
        return self._http_client.request(
            request_type='put',
            url=f"{self._base_url}/{id}",
            payload=request
        )

    def create_stream_subscription(self, subscriptions:List[StreamSubscriptionRequestModel]) -> MessageModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/createStreamSubscription"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/streaming/subscriptions",
            payload=subscriptions
        )

    def delete_stream_subscription(self, id:str) -> MessageModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/DeleteStreamSubscription"""
        return self._http_client.request(
            request_type='delete',
            url=f"{self._base_url}/streaming/subscriptions/{id}"
        )

    def get_streaming_subscriptions(self) -> StreamSubscriptionDataModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getStreamSubscriptions"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/streaming/subscriptions"
        )

    def set_stream_destination(self, connectionString:str) -> MessageModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/setStreanDestination"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/streaming/subscriptions",
            payload={
                'connectionString': connectionString
            }
        )

    def delete_timeseries_by_id(self, id:str) -> MessageModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/deleteTimeseriesById"""
        return self._http_client.request(
            request_type='delete',
            url=f"{self._base_url}/{id}"
        )

    def delete_data(self, id:str, startTime:Optional[str]=None, endTime:Optional[str]=None) -> MessageModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/deleteData"""
        params = {}
        if startTime is not None:
            params['startTime'] = startTime
        if endTime is not None:
            params['endTime'] = endTime
        return self._http_client.request(
            request_type='delete',
            url=f"{self._base_url}/{id}/data",
            params=params
        )

    def get_facilities(self) -> FacilityDataModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getFacility"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/facility/counters"
        )

    def get_facility_by_name(self, name:str) -> FacilityDataModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-6/operations/getFacilityByName"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/facility/{name}/counters"
        )