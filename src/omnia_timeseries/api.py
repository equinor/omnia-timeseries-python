from typing import List, Literal, Optional
from azure.identity._internal.msal_credentials import MsalCredential
from omnia_timeseries.http_client import HttpClient, ContentType
from omnia_timeseries.models import (
    DatapointModel,
    DatapointsItemsModel, DatapointsPostRequestModel,
    FacilityDataModel, GetAggregatesResponseModel, GetDatapointsResponseModel, GetHistoryResponseModel, GetMultipleDatapointsRequestItem, GetTimeseriesResponseModel,
    SourceDataModel,
    MessageModel,
    StreamSubscriptionRequestModel,
    StreamSubscriptionDataModel,
    TimeseriesPatchRequestItem, TimeseriesRequestItem
)
import logging
from enum import Enum

TimeseriesVersion = Literal["1.6", "1.7"]

logger = logging.getLogger(__name__)

class FederationSource(Enum):
    """
    Set source that Omnia Timeseries API will use when executing a given query:
    - Use `IMS` to query the underlying PI or IP21 IMS source. 
    - Use `TSDB` for Omnia timeseries database which should be up-to-date with IMS.
    - Use `DataLake` for historic Omnia timeseries data which is 2 days behind `TSDB` and may contain data older than `TSDB`. 
    """
    #Ensure that Enum string value is returned instead of Enum full name
    def __str__(self):
        return self.value
    
    IMS = "IMS"
    TSDB = "TSDB"
    DataLake = "DataLake"

class TimeseriesEnvironment:
    def __init__(self, resource_id: str, base_url: str):
        '''
        Wrapper class for defining which timeseries environment the TimeseriesAPI client will interface to

        :param str resource_id: Resource/client id of API app registration (Azure SPN)
        :param str base_url: Baze url of API
        '''
        self._resource_id = resource_id
        self._base_url = base_url

    @classmethod
    def Dev(cls, version: TimeseriesVersion = "1.7"):
        '''
        Sets up non-production dev environment
        '''
        return cls(
            resource_id="32f2a909-8a98-4eb8-b22d-1208d9350cb0",
            base_url=f"https://api-dev.gateway.equinor.com/plant/timeseries/v{version}"
        )

    @classmethod
    def Test(cls, version: TimeseriesVersion = "1.7"):
        '''
        Sets up non-production environment
        '''
        return cls(
            resource_id="32f2a909-8a98-4eb8-b22d-1208d9350cb0",
            base_url=f"https://api-test.gateway.equinor.com/plant/timeseries/v{version}"
        )

    @classmethod
    def Prod(cls, version: TimeseriesVersion = "1.7"):
        '''
        Sets up production environment
        '''
        return cls(
            resource_id="141369bd-3dca-4b55-825b-56ad4a69b1fc",
            base_url=f"https://api.gateway.equinor.com/plant/timeseries/v{version}"
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

    :param MsalCredential azure_credential: Azure credential instance used for authenticating
    :param TimeseriesEnvironment environment: API deployment environment
    """

    def __init__(self, azure_credential: MsalCredential, environment: TimeseriesEnvironment):
        self._http_client = HttpClient(
            azure_credential=azure_credential, resource_id=environment.resource_id)
        self._base_url = environment.base_url.rstrip('/')

    def write_data(self, id: str, data: DatapointsPostRequestModel, write_async: Optional[bool] = None) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=writeData"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/{id}/data",
            params={'async': write_async} if write_async is not None else None,
            payload=data
        )

    def write_multiple(self, items: DatapointsItemsModel, write_async: Optional[bool] = None) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=writeMultipleData"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/data",
            params={'async': write_async} if write_async is not None else None,
            payload=items
        )

    def get_datapoints(
            self,
            id: str,
            startTime: Optional[str] = None,
            endTime: Optional[str] = None,
            status: Optional[List[int]] = None,
            includeOutsidePoints: Optional[bool] = None,
            limit: Optional[int] = None,
            continuationToken: Optional[str] = None,
            federationSource: Optional[Enum] = None,
            accept: ContentType = "application/json") -> GetDatapointsResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetData"""
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
        if federationSource is not None:
            params['federationSource'] = federationSource
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/data",
            accept=accept,
            params=params
        )

    def get_datapoints_by_name(
            self,
            name: str,
            facility: str,
            terminal: Optional[str] = None,
            startTime: Optional[str] = None,
            endTime: Optional[str] = None,
            status: Optional[List[int]] = None,
            includeOutsidePoints: Optional[bool] = None,
            limit: Optional[int] = None,
            continuationToken: Optional[str] = None,
            federationSource: Optional[Enum] = None,
            accept: ContentType = "application/json") -> GetDatapointsResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-7/operations/getDataByName"""
        params = {}
        params["name"] = name
        params["facility"] = facility
        if terminal is not None:
            params["terminal"] = terminal
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
        if federationSource is not None:
            params['federationSource'] = federationSource
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/query/data",
            accept=accept,
            params=params
        )

    def get_multi_datapoints(
            self,
            request: List[GetMultipleDatapointsRequestItem],
            continuationToken: Optional[str] = None,
            federationSource: Optional[Enum] = None,
            accept: ContentType = "application/json") -> GetAggregatesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetMultipleData"""
        params = {}
        if continuationToken is not None:
            params['continuationToken'] = continuationToken
        if federationSource is not None:
            params['federationSource'] = federationSource
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/query/data",
            accept=accept,
            params=params,
            payload=request
        )

    def get_aggregates(
            self,
            id: str,
            aggregateFunction: List[Literal['avg', 'min', 'max', 'sum', 'stddev', 'count', 'first', 'last']],
            startTime: Optional[str] = None,
            endTime: Optional[str] = None,
            status: Optional[List[int]] = None,
            processingInterval: Optional[str] = None,
            fill: Optional[str] = None,
            limit: Optional[int] = None,
            continuationToken: Optional[str] = None,
            federationSource: Optional[Enum] = None,
            accept: ContentType = "application/json") -> GetAggregatesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetAggregatedData"""
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
        if federationSource is not None:
            params['federationSource'] = federationSource
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/data/aggregates",
            accept=accept,
            params=params
        )

    def get_first_datapoint(
            self,
            id: str,
            afterTime: Optional[str] = None,
            beforeTime: Optional[str] = None,
            status: Optional[List[int]] = None,
            federationSource: Optional[Enum] = None,
            accept: ContentType = "application/json") -> DatapointModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFirst"""
        params = {}
        if afterTime is not None:
            params['afterTime'] = afterTime
        if beforeTime is not None:
            params['beforeTime'] = beforeTime
        if status is not None:
            params['status'] = status
        if federationSource is not None:
            params['federationSource'] = federationSource
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/data/first",
            accept=accept,
            params=params
        )

    def get_latest_datapoint(
            self,
            id: str,
            afterTime: Optional[str] = None,
            beforeTime: Optional[str] = None,
            status: Optional[List[int]] = None,
            federationSource: Optional[Enum] = None,
            accept: ContentType = "application/json") -> GetDatapointsResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetLatest"""
        params = {}
        if afterTime is not None:
            params['afterTime'] = afterTime
        if beforeTime is not None:
            params['beforeTime'] = beforeTime
        if status is not None:
            params['status'] = status
        if federationSource is not None:
            params['federationSource'] = federationSource
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/data/latest",
            accept=accept,
            params=params
        )

    def get_first_multi_datapoint(self,
                                  request: List[GetMultipleDatapointsRequestItem],
                                  federationSource: Optional[Enum] = None,
                                  accept: ContentType = "application/json") -> GetDatapointsResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetMultipleFirst"""
        params = {}
        if federationSource is not None:
            params['federationSource'] = federationSource
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/query/data/first",
            accept=accept,
            payload=request,
            params=params
        )

    def get_latest_multi_datapoint(self,
                                   request: List[GetMultipleDatapointsRequestItem],
                                   federationSource: Optional[Enum] = None,
                                   accept: ContentType = "application/json") -> GetDatapointsResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetMultipleLatest"""
        params = {}
        if federationSource is not None:
            params['federationSource'] = federationSource
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/query/data/latest",
            accept=accept,
            payload=request,
            params=params
        )

    def get_history(self, id: str) -> GetHistoryResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=getHistory"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}/history",
        )

    def get_timeseries(
            self,
            name: Optional[str] = None,
            externalId: Optional[str] = None,
            source: Optional[str] = None,
            assetId: Optional[str] = None,
            facility: Optional[str] = None,
            limit: Optional[int] = None,
            continuationToken: Optional[str] = None,
            **kwargs) -> GetTimeseriesResponseModel:
        """
        https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=Getall
        Note that maximum result set is 100.000 items.
        """
        params = kwargs or {}
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
            query: Optional[str] = None,
            name: Optional[str] = None,
            externalId: Optional[str] = None,
            source: Optional[str] = None,
            assetId: Optional[str] = None,
            facility: Optional[str] = None,
            description: Optional[str] = None,
            unit: Optional[str] = None,
            continuationToken: Optional[str] = None,
            **kwargs) -> GetTimeseriesResponseModel:
        """
        Without query: https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetSearch
        With query: https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetSearchByQuery
        Note that maximum result set is 100.000 items.
        """
        params = kwargs or {}
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

    def get_timeseries_by_id(self, id: str) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=getTimeseriesById"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/{id}"
        )

    def post_timeseries(self, request: TimeseriesRequestItem) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=postTimeseries"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}",
            payload=request
        )

    def get_or_add_timeseries(self, request: List[TimeseriesRequestItem]) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetOrAddTimeseries"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/getoradd",
            payload=request
        )

    def patch_timeseries(self, id: str, request: TimeseriesPatchRequestItem) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=patchTimeseries"""
        return self._http_client.request(
            request_type='patch',
            url=f"{self._base_url}/{id}",
            payload=request
        )

    def put_timeseries(self, id: str, request: TimeseriesRequestItem) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=puttimeseries"""
        return self._http_client.request(
            request_type='put',
            url=f"{self._base_url}/{id}",
            payload=request
        )

    def create_stream_subscription(self, subscriptions: List[StreamSubscriptionRequestModel]) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=CreateSubscriptions"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/streaming/subscriptions",
            payload=subscriptions
        )

    def delete_stream_subscription(self, id: str) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=DeleteSubscriptions"""
        return self._http_client.request(
            request_type='delete',
            url=f"{self._base_url}/streaming/subscriptions/{id}"
        )

    def get_streaming_subscriptions(self) -> StreamSubscriptionDataModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetSubscriptions"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/streaming/subscriptions"
        )

    def set_stream_destination(self, connectionString: str) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=SetRealTimeDestination"""
        return self._http_client.request(
            request_type='post',
            url=f"{self._base_url}/streaming/destination",
            payload={
                'connectionString': connectionString
            }
        )

    def delete_timeseries_by_id(self, id: str) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=DeleteTimeseries"""
        return self._http_client.request(
            request_type='delete',
            url=f"{self._base_url}/{id}"
        )

    def delete_data(self, id: str, startTime: Optional[str] = None, endTime: Optional[str] = None) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=deleteData"""
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
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFacets"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/facets/facility"
        )

    def get_sources(self) ->  SourceDataModel:        
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFacets"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/facets/source"
        )
        
    def get_sources_by_facility(self, facility: str) ->  SourceDataModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFacets"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/facets/source?facility={facility}"
        )

    def get_facilities_by_source(self, source: str) -> FacilityDataModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFacets"""
        return self._http_client.request(
            request_type='get',
            url=f"{self._base_url}/facets/facility?source={source}"
        )