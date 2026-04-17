from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
from azure.core.credentials import TokenCredential
from omnia_timeseries.http_client import HttpClient, ContentType
from omnia_timeseries.models import (
    DatapointModel,
    DatapointsItemsModel,
    DatapointsPostRequestModel,
    FacilityDataModel,
    GetAggregatesResponseModel,
    GetDatapointsResponseModel,
    GetHistoryResponseModel,
    GetMultipleDatapointsRequestItem,
    GetTimeseriesResponseModel,
    GetIMSMetadataResponseModel,
    SourceDataModel,
    MessageModel,
    StreamSubscriptionRequestModel,
    StreamSubscriptionDataModel,
    SubscriptionCounterModel,
    SubscriptionPatchRequestItem,
    TimeseriesPatchRequestItem,
    TimeseriesRequestItem,
)
import logging
from enum import Enum

IMSMetadataVersion = Literal["1.3"]
IMSSubscriptionsVersion = Literal["1.2"]
TimeseriesVersion = Literal["1.6", "1.7"]

logger = logging.getLogger(__name__)


class FederationSource(Enum):
    """
    Set source that Omnia Timeseries API will use when executing a given query:
    - Use `IMS` to query the underlying PI or IP21 IMS source.
    - Use `TSDB` for Omnia timeseries database which should be up-to-date with IMS.
    - Use `DataLake` for historic Omnia timeseries data which is 2 days behind `TSDB` and may contain data older than `TSDB`.
    """

    # Ensure that Enum string value is returned instead of Enum full name
    def __str__(self):
        return self.value

    IMS = "IMS"
    TSDB = "TSDB"
    DataLake = "DataLake"

# Internal enum to represent environment chosen by user via TimeseriesEnvironment
class Environment(Enum):
    Dev = "dev"
    Test = "test"
    Prod = "prod"

# User-facing, immutable token accepted by all APIs with Python v3.8 slots-like behaviour
@dataclass(frozen=True)
class TimeseriesEnvironment:
    __slots__ = ("kind",)
    kind: Environment

    @classmethod
    def Dev(cls) -> "TimeseriesEnvironment":
        """
        Set non-production dev environment
        """
        return cls(kind=Environment.Dev)

    @classmethod
    def Test(cls) -> "TimeseriesEnvironment":
        """
        Set non-production test environment
        """
        return cls(kind=Environment.Test)

    @classmethod
    def Prod(cls) -> "TimeseriesEnvironment":
        """
        Set production environment
        """
        return cls(kind=Environment.Prod)

class IMSMetadataApiEnvironment:
    def __init__(self, environment: TimeseriesEnvironment, version: IMSMetadataVersion = "1.3"):
        """
        Wrapper class for defining which environment the IMS Metadata API client will interface to

        :param TimeseriesEnvironment environment: Value with environment chosen as dev, test or prod
        """

        # Prepare API connection details
        if environment.kind is Environment.Dev:
            self._resource_id = "310547f5-022b-4fb5-b13e-2b468b8bf658"
            self._base_url = f"https://api-dev.gateway.equinor.com/plant/ims-metadata/v{version}"

        if environment.kind is Environment.Test:
            self._resource_id = "310547f5-022b-4fb5-b13e-2b468b8bf658"
            self._base_url = f"https://api-test.gateway.equinor.com/plant/ims-metadata/v{version}"

        if environment.kind is Environment.Prod:
            self._resource_id = "71415e4e-7131-4a81-9596-f921978cdbee"
            self._base_url = f"https://api.gateway.equinor.com/plant/ims-metadata/v{version}"

        # Safeguard in case of new, unsupported environment
        if not hasattr(self, "_resource_id") or not hasattr(self, "_base_url"):
            raise ValueError(f"Unsupported environment: {environment.kind!r}")

    @property
    def resource_id(self) -> str:
        return self._resource_id

    @property
    def base_url(self) -> str:
        return self._base_url

class IMSSubscriptionsAPIEnvironment:
    def __init__(self, environment: TimeseriesEnvironment, version: IMSSubscriptionsVersion = "1.2"):
        """
        Wrapper class for defining which environment the IMS Subscriptions API client will interface to

        :param TimeseriesEnvironment environment: Value with environment chosen as dev, test or prod
        """

        # Prepare API connection details
        if environment.kind is Environment.Dev:
            self._resource_id = "789d768e-32ac-417b-b286-be5e0d460809"
            self._base_url = f"https://api-dev.gateway.equinor.com/plant/ims-subscriptions/v{version}"

        if environment.kind is Environment.Test:
            self._resource_id = "789d768e-32ac-417b-b286-be5e0d460809"
            self._base_url = f"https://api-test.gateway.equinor.com/plant/ims-subscriptions/v{version}"

        if environment.kind is Environment.Prod:
            self._resource_id = "cae23674-f25d-40a2-b9e4-81649b33b957"
            self._base_url = f"https://api.gateway.equinor.com/plant/ims-subscriptions/v{version}"

        # Safeguard in case of new, unsupported environment
        if not hasattr(self, "_resource_id") or not hasattr(self, "_base_url"):
            raise ValueError(f"Unsupported environment: {environment.kind!r}")

    @property
    def resource_id(self) -> str:
        return self._resource_id

    @property
    def base_url(self) -> str:
        return self._base_url

class IMSSubscriptionsManagementAPIEnvironment:
    def __init__(self, environment: TimeseriesEnvironment, version: IMSSubscriptionsVersion = "1.2"):
        """
        Wrapper class for defining which environment the IMS Subscriptions Management API client will interface to

        :param TimeseriesEnvironment environment: Value with environment chosen as dev, test or prod
        """

        # Prepare API connection details
        if environment.kind is Environment.Dev:
            self._resource_id = "789d768e-32ac-417b-b286-be5e0d460809"
            self._base_url = f"https://api-dev.gateway.equinor.com/plant/ims-subscriptions-management/v{version}"

        if environment.kind is Environment.Test:
            self._resource_id = "789d768e-32ac-417b-b286-be5e0d460809"
            self._base_url = f"https://api-test.gateway.equinor.com/plant/ims-subscriptions-management/v{version}"

        if environment.kind is Environment.Prod:
            self._resource_id = "cae23674-f25d-40a2-b9e4-81649b33b957"
            self._base_url = f"https://api.gateway.equinor.com/plant/ims-subscriptions-management/v{version}"

        # Safeguard in case of new, unsupported environment
        if not hasattr(self, "_resource_id") or not hasattr(self, "_base_url"):
            raise ValueError(f"Unsupported environment: {environment.kind!r}")

    @property
    def resource_id(self) -> str:
        return self._resource_id

    @property
    def base_url(self) -> str:
        return self._base_url

class TimeseriesApiEnvironment:
    def __init__(self, environment: TimeseriesEnvironment, version: TimeseriesVersion = "1.7"):
        """
        Wrapper class for defining which environment the Timeseries API client will interface to

        :param TimeseriesEnvironment environment: Value with environment chosen as dev, test or prod
        """

        # Prepare API connection details
        if environment.kind is Environment.Dev:
            self._resource_id = "32f2a909-8a98-4eb8-b22d-1208d9350cb0"
            self._base_url = f"https://api-dev.gateway.equinor.com/plant/timeseries/v{version}"

        if environment.kind is Environment.Test:
            self._resource_id = "32f2a909-8a98-4eb8-b22d-1208d9350cb0"
            self._base_url = f"https://api-test.gateway.equinor.com/plant/timeseries/v{version}"

        if environment.kind is Environment.Prod:
            self._resource_id = "141369bd-3dca-4b55-825b-56ad4a69b1fc"
            self._base_url = f"https://api.gateway.equinor.com/plant/timeseries/v{version}"

        # Safeguard in case of new, unsupported environment
        if not hasattr(self, "_resource_id") or not hasattr(self, "_base_url"):
            raise ValueError(f"Unsupported environment: {environment.kind!r}")

    @property
    def resource_id(self) -> str:
        return self._resource_id

    @property
    def base_url(self) -> str:
        return self._base_url

class IMSMetadataAPI:
    """
    Wrapper class for interacting with the Omnia Industrial IIoT IMS Metadata API.
    For more information, see https://github.com/equinor/OmniaPlant/wiki or consult with the Omnia IIoT team.

    :param MsalCredential azure_credential: Azure credential instance used for authenticating
    :param TimeseriesEnvironment environment: API deployment environment
    """

    def __init__(
        self, azure_credential: TokenCredential, environment: TimeseriesEnvironment
    ):
        if not isinstance(environment, TimeseriesEnvironment):
            raise TypeError(f"Environment must be TimeseriesEnvironment, got: {type(environment).__name__}")
        apiEnvironment=IMSMetadataApiEnvironment(environment)
        self._http_client = HttpClient(
            azure_credential=azure_credential, resource_id=apiEnvironment.resource_id
        )
        self._base_url = apiEnvironment.base_url.rstrip("/")

    def search(
        self,
        tag: Optional[str] = None,
        uid: Optional[str] = None,
        continuationToken: Optional[str] = None,
        **kwargs,
    ) -> GetIMSMetadataResponseModel:
        """
        Search IMS Metadata API
        """
        params = kwargs or {}
        if tag is not None:
            params["tag"] = tag
        if uid is not None:
            params["uid"] = uid
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        url = (
            f"{self._base_url}/search"
        )
        return self._http_client.request(request_type="get", url=url, params=params)

class IMSSubscriptionsAPI:
    """
    Wrapper class for interacting with the Omnia Industrial IIoT IMS Subscriptions API.
    For more information, see https://github.com/equinor/OmniaPlant/wiki or consult with the Omnia IIoT team.

    :param MsalCredential azure_credential: Azure credential instance used for authenticating
    :param TimeseriesEnvironment environment: API deployment environment
    """

    def __init__(
        self, azure_credential: TokenCredential, environment: TimeseriesEnvironment
    ):
        if not isinstance(environment, TimeseriesEnvironment):
            raise TypeError(f"Environment must be TimeseriesEnvironment, got: {type(environment).__name__}")
        apiEnvironment=IMSSubscriptionsAPIEnvironment(environment)
        self._http_client = HttpClient(
            azure_credential=azure_credential, resource_id=apiEnvironment.resource_id
        )
        self._base_url = apiEnvironment.base_url.rstrip("/")

    def search(
        self,
        limit: Optional[int] = 1000,
        continuationToken: Optional[str] = None,
        **kwargs,
    ) -> GetIMSMetadataResponseModel:
        """
        Search IMS Subscriptions API
        """
        params = kwargs or {}
        if limit is not None:
            params["limit"] = limit
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        url = (
            f"{self._base_url}"
        )
        return self._http_client.request(request_type="get", url=url, params=params)

    def search_by_uid(
        self,
        uid: Optional[str] = None,
        continuationToken: Optional[str] = None,
        **kwargs,
    ) -> GetIMSMetadataResponseModel:
        """
        Search IMS Subscriptions API
        """
        params = kwargs or {}
        if uid is not None:
            params["uid"] = uid
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        url = (
            f"{self._base_url}/uid/{uid}"
        )
        return self._http_client.request(request_type="get", url=url, params=params)

    def search_by_timeseries_id(
        self,
        timeseriesId: Optional[str] = None,
        continuationToken: Optional[str] = None,
        **kwargs,
    ) -> GetIMSMetadataResponseModel:
        """
        Search IMS Subscriptions API
        """
        params = kwargs or {}
        if timeseriesId is not None:
            params["timeseriesId"] = timeseriesId
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        url = (
            f"{self._base_url}/timeseriesId/{timeseriesId}"
        )
        return self._http_client.request(request_type="get", url=url, params=params)

    def search_by_system_code(
        self,
        systemCode: str,
        **kwargs,
    ) -> SubscriptionCounterModel:
        """
        Search IMS Subscriptions API
        """
        params = kwargs or {}
        url = (
            f"{self._base_url}/{systemCode}"
        )
        return self._http_client.request(request_type="get", url=url, params=params)

class IMSSubscriptionsManagementAPI:
    """
    Wrapper class for interacting with the Omnia Industrial IIoT IMS Subscriptions Management API.
    For more information, see https://github.com/equinor/OmniaPlant/wiki or consult with the Omnia IIoT team.

    :param MsalCredential azure_credential: Azure credential instance used for authenticating
    :param TimeseriesEnvironment environment: API deployment environment
    """

    def __init__(
        self, azure_credential: TokenCredential, environment: TimeseriesEnvironment
    ):
        if not isinstance(environment, TimeseriesEnvironment):
            raise TypeError(f"Environment must be TimeseriesEnvironment, got: {type(environment).__name__}")
        apiEnvironment=IMSSubscriptionsManagementAPIEnvironment(environment)
        self._http_client = HttpClient(
            azure_credential=azure_credential, resource_id=apiEnvironment.resource_id
        )
        self._base_url = apiEnvironment.base_url.rstrip("/")

    def get_subscription_counter_by_system_code(
        self,
        systemCode: str,
        **kwargs,
    ) -> SubscriptionCounterModel:
        """
        Search IMS Subscriptions Management API
        """
        params = kwargs or {}
        url = (
            f"{self._base_url}/{systemCode}/counter"
        )
        return self._http_client.request(request_type="get", url=url, params=params)

    def patch_subscription_by_uid(
        self,
        uid: str,
        request: SubscriptionPatchRequestItem
    ) -> GetIMSMetadataResponseModel:
        """
        Search IMS Subscriptions Management API
        """
        url = (
            f"{self._base_url}/uid/{uid}"
        )
        return self._http_client.request(request_type="patch", url=url, payload=request)

class TimeseriesAPI:
    """
    Wrapper class for interacting with the Omnia Industrial IIoT Timeseries API.
    For more information, see https://github.com/equinor/OmniaPlant/wiki or consult with the Omnia IIoT team.

    :param TokenCredential azure_credential: Azure token credential instance used for authenticating
    :param TimeseriesEnvironment environment: API deployment environment
    """

    def __init__(
        self, azure_credential: TokenCredential, environment: TimeseriesEnvironment
    ):
        if not isinstance(environment, TimeseriesEnvironment):
            raise TypeError(f"Environment must be TimeseriesEnvironment, got: {type(environment).__name__}")
        apiEnvironment=TimeseriesApiEnvironment(environment)
        self._http_client = HttpClient(
            azure_credential=azure_credential, resource_id=apiEnvironment.resource_id
        )
        self._base_url = apiEnvironment.base_url.rstrip("/")
        self._debug_mode = False

    def _add_debug_param(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if self._debug_mode:
            params["debug"] = True
        return params

    def write_data(
        self,
        id: str,
        data: DatapointsPostRequestModel,
        write_async: Optional[bool] = None,
    ) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=writeData"""
        return self._http_client.request(
            request_type="post",
            url=f"{self._base_url}/{id}/data",
            params={"async": write_async} if write_async is not None else None,
            payload=data,
        )

    def write_multiple(
        self, items: DatapointsItemsModel, write_async: Optional[bool] = None
    ) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=writeMultipleData"""
        return self._http_client.request(
            request_type="post",
            url=f"{self._base_url}/data",
            params={"async": write_async} if write_async is not None else None,
            payload=items,
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
        accept: ContentType = "application/json",
    ) -> GetDatapointsResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetData"""
        params = {}
        if startTime is not None:
            params["startTime"] = startTime
        if endTime is not None:
            params["endTime"] = endTime
        if status is not None:
            params["status"] = status
        if includeOutsidePoints is not None:
            params["includeOutsidePoints"] = includeOutsidePoints
        if limit is not None:
            params["limit"] = limit
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        if federationSource is not None:
            params["federationSource"] = federationSource
        params = self._add_debug_param(params)
        return self._http_client.request(
            request_type="get",
            url=f"{self._base_url}/{id}/data",
            accept=accept,
            params=params,
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
        accept: ContentType = "application/json",
    ) -> GetDatapointsResponseModel:
        """https://api.equinor.com/docs/services/Timeseries-api-v1-7/operations/getDataByName"""
        params = {}
        params["name"] = name
        params["facility"] = facility
        if terminal is not None:
            params["terminal"] = terminal
        if startTime is not None:
            params["startTime"] = startTime
        if endTime is not None:
            params["endTime"] = endTime
        if status is not None:
            params["status"] = status
        if includeOutsidePoints is not None:
            params["includeOutsidePoints"] = includeOutsidePoints
        if limit is not None:
            params["limit"] = limit
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        if federationSource is not None:
            params["federationSource"] = federationSource
        params = self._add_debug_param(params)
        return self._http_client.request(
            request_type="get",
            url=f"{self._base_url}/query/data",
            accept=accept,
            params=params,
        )

    def get_multi_datapoints(
        self,
        request: List[GetMultipleDatapointsRequestItem],
        continuationToken: Optional[str] = None,
        federationSource: Optional[Enum] = None,
        accept: ContentType = "application/json",
        alignToCache: Optional[bool] = None,
    ) -> GetAggregatesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetMultipleData"""
        params = {}
        if alignToCache is not None:
            params["alignToCache"] = alignToCache
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        if federationSource is not None:
            params["federationSource"] = federationSource
        params = self._add_debug_param(params)
        return self._http_client.request(
            request_type="post",
            url=f"{self._base_url}/query/data",
            accept=accept,
            params=params,
            payload=request,
        )

    def get_aggregates(
        self,
        id: str,
        aggregateFunction: List[
            Literal["avg", "min", "max", "sum", "stddev", "count", "first", "last"]
        ],
        startTime: Optional[str] = None,
        endTime: Optional[str] = None,
        status: Optional[List[int]] = None,
        processingInterval: Optional[str] = None,
        fill: Optional[str] = None,
        limit: Optional[int] = None,
        continuationToken: Optional[str] = None,
        federationSource: Optional[Enum] = None,
        accept: ContentType = "application/json",
        alignToCache: Optional[bool] = None,
    ) -> GetAggregatesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetAggregatedData"""
        params = {}
        if aggregateFunction is not None:
            params["aggregateFunction"] = aggregateFunction
        if startTime is not None:
            params["startTime"] = startTime
        if endTime is not None:
            params["endTime"] = endTime
        if status is not None:
            params["status"] = status
        if processingInterval is not None:
            params["processingInterval"] = processingInterval
        if fill is not None:
            params["fill"] = fill
        if limit is not None:
            params["limit"] = limit
        if alignToCache is not None:
            params["alignToCache"] = alignToCache
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        if federationSource is not None:
            params["federationSource"] = federationSource
        params = self._add_debug_param(params)
        return self._http_client.request(
            request_type="get",
            url=f"{self._base_url}/{id}/data/aggregates",
            accept=accept,
            params=params,
        )

    def get_first_datapoint(
        self,
        id: str,
        afterTime: Optional[str] = None,
        beforeTime: Optional[str] = None,
        status: Optional[List[int]] = None,
        federationSource: Optional[Enum] = None,
        accept: ContentType = "application/json",
    ) -> DatapointModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFirst"""
        params = {}
        if afterTime is not None:
            params["afterTime"] = afterTime
        if beforeTime is not None:
            params["beforeTime"] = beforeTime
        if status is not None:
            params["status"] = status
        if federationSource is not None:
            params["federationSource"] = federationSource
        params = self._add_debug_param(params)
        return self._http_client.request(
            request_type="get",
            url=f"{self._base_url}/{id}/data/first",
            accept=accept,
            params=params,
        )

    def get_latest_datapoint(
        self,
        id: str,
        afterTime: Optional[str] = None,
        beforeTime: Optional[str] = None,
        status: Optional[List[int]] = None,
        federationSource: Optional[Enum] = None,
        accept: ContentType = "application/json",
    ) -> GetDatapointsResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetLatest"""
        params = {}
        if afterTime is not None:
            params["afterTime"] = afterTime
        if beforeTime is not None:
            params["beforeTime"] = beforeTime
        if status is not None:
            params["status"] = status
        if federationSource is not None:
            params["federationSource"] = federationSource
        params = self._add_debug_param(params)
        return self._http_client.request(
            request_type="get",
            url=f"{self._base_url}/{id}/data/latest",
            accept=accept,
            params=params,
        )

    def get_first_multi_datapoint(
        self,
        request: List[GetMultipleDatapointsRequestItem],
        federationSource: Optional[Enum] = None,
        accept: ContentType = "application/json",
    ) -> GetDatapointsResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetMultipleFirst"""
        params = {}
        if federationSource is not None:
            params["federationSource"] = federationSource
        return self._http_client.request(
            request_type="post",
            url=f"{self._base_url}/query/data/first",
            accept=accept,
            payload=request,
            params=params,
        )

    def get_latest_multi_datapoint(
        self,
        request: List[GetMultipleDatapointsRequestItem],
        federationSource: Optional[Enum] = None,
        accept: ContentType = "application/json",
    ) -> GetDatapointsResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetMultipleLatest"""
        params = {}
        if federationSource is not None:
            params["federationSource"] = federationSource
        params = self._add_debug_param(params)
        return self._http_client.request(
            request_type="post",
            url=f"{self._base_url}/query/data/latest",
            accept=accept,
            payload=request,
            params=params,
        )

    def get_history(self, id: str) -> GetHistoryResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=getHistory"""
        return self._http_client.request(
            request_type="get",
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
        **kwargs,
    ) -> GetTimeseriesResponseModel:
        """
        https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=Getall
        Note that maximum result set is 100.000 items.
        """
        params = kwargs or {}
        if name is not None:
            params["name"] = name
        if externalId is not None:
            params["externalId"] = externalId
        if source is not None:
            params["source"] = source
        if assetId is not None:
            params["assetId"] = assetId
        if facility is not None:
            params["facility"] = facility
        if limit is not None:
            params["limit"] = limit
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        return self._http_client.request(
            request_type="get", url=f"{self._base_url}", params=params
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
        **kwargs,
    ) -> GetTimeseriesResponseModel:
        """
        Without query: https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetSearch
        With query: https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetSearchByQuery
        Note that maximum result set is 100.000 items.
        """
        params = kwargs or {}
        if name is not None:
            params["name"] = name
        if externalId is not None:
            params["externalId"] = externalId
        if source is not None:
            params["source"] = source
        if assetId is not None:
            params["assetId"] = assetId
        if facility is not None:
            params["facility"] = facility
        if description is not None:
            params["description"] = description
        if unit is not None:
            params["unit"] = unit
        if continuationToken is not None:
            params["continuationToken"] = continuationToken
        url = (
            f"{self._base_url}/search"
            if query is None
            else f"{self._base_url}/search/{query}"
        )
        return self._http_client.request(request_type="get", url=url, params=params)

    def get_timeseries_by_id(self, id: str) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=getTimeseriesById"""
        return self._http_client.request(
            request_type="get", url=f"{self._base_url}/{id}"
        )

    def post_timeseries(
        self, request: TimeseriesRequestItem
    ) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=postTimeseries"""
        return self._http_client.request(
            request_type="post", url=f"{self._base_url}", payload=request
        )

    def get_or_add_timeseries(
        self, request: List[TimeseriesRequestItem]
    ) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetOrAddTimeseries"""
        return self._http_client.request(
            request_type="post", url=f"{self._base_url}/getoradd", payload=request
        )

    def patch_timeseries(
        self, id: str, request: TimeseriesPatchRequestItem
    ) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=patchTimeseries"""
        return self._http_client.request(
            request_type="patch", url=f"{self._base_url}/{id}", payload=request
        )

    def put_timeseries(
        self, id: str, request: TimeseriesRequestItem
    ) -> GetTimeseriesResponseModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=puttimeseries"""
        return self._http_client.request(
            request_type="put", url=f"{self._base_url}/{id}", payload=request
        )

    def create_stream_subscription(
        self, subscriptions: List[StreamSubscriptionRequestModel]
    ) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=CreateSubscriptions"""
        return self._http_client.request(
            request_type="post",
            url=f"{self._base_url}/streaming/subscriptions",
            payload=subscriptions,
        )

    def delete_stream_subscription(self, id: str) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=DeleteSubscriptions"""
        return self._http_client.request(
            request_type="delete", url=f"{self._base_url}/streaming/subscriptions/{id}"
        )

    def get_streaming_subscriptions(self) -> StreamSubscriptionDataModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetSubscriptions"""
        return self._http_client.request(
            request_type="get", url=f"{self._base_url}/streaming/subscriptions"
        )

    def set_stream_destination(self, connectionString: str) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=SetRealTimeDestination"""
        return self._http_client.request(
            request_type="post",
            url=f"{self._base_url}/streaming/destination",
            payload={"connectionString": connectionString},
        )

    def delete_timeseries_by_id(self, id: str) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=DeleteTimeseries"""
        return self._http_client.request(
            request_type="delete", url=f"{self._base_url}/{id}"
        )

    def delete_data(
        self, id: str, startTime: Optional[str] = None, endTime: Optional[str] = None
    ) -> MessageModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=deleteData"""
        params = {}
        if startTime is not None:
            params["startTime"] = startTime
        if endTime is not None:
            params["endTime"] = endTime
        return self._http_client.request(
            request_type="delete", url=f"{self._base_url}/{id}/data", params=params
        )

    def get_facilities(self) -> FacilityDataModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFacets"""
        return self._http_client.request(
            request_type="get", url=f"{self._base_url}/facets/facility"
        )

    def get_sources(self) -> SourceDataModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFacets"""
        return self._http_client.request(
            request_type="get", url=f"{self._base_url}/facets/source"
        )

    def get_sources_by_facility(self, facility: str) -> SourceDataModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFacets"""
        return self._http_client.request(
            request_type="get",
            url=f"{self._base_url}/facets/source?facility={facility}",
        )

    def get_facilities_by_source(self, source: str) -> FacilityDataModel:
        """https://api.equinor.com/api-details#api=Timeseries-api-v1-7&operation=GetFacets"""
        return self._http_client.request(
            request_type="get", url=f"{self._base_url}/facets/facility?source={source}"
        )
