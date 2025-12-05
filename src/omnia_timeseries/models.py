from typing import List, Optional, TypedDict, Dict, Any, Literal
from requests.models import Response
import json


class MessageModel(TypedDict):
    statusCode: int
    message: str
    traceId: str


class DatapointModel(TypedDict):
    time: str
    value: float
    status: int


class DatapointsPostRequestModel(TypedDict):
    datapoints: List[DatapointModel]


class DatapointsItemModel(TypedDict):
    id: str
    datapoints: List[DatapointModel]


class DatapointsItemsModel(TypedDict):
    items: List[DatapointsItemModel]


class GetDatapointsResponseModel(TypedDict):
    data: DatapointsItemsModel
    count: Optional[int]
    continuationToken: Optional[str]
    federated: Optional[bool]


class GetMultipleDatapointsRequestItem(TypedDict, total=False):
    id: str
    startTime: Optional[str]
    endTime: Optional[str]
    limit: Optional[int]
    statusFilter: Optional[List[int]]
    includeOutsidePoints: Optional[bool]
    fill: Optional[str]
    aggregateFunctions: Optional[
        List[Literal["avg", "min", "max", "sum", "stddev", "count", "first", "last"]]
    ]
    processingInterval: Optional[str]
    continuationToken: Optional[str]


class AggregateModel(TypedDict, total=False):
    time: str
    avg: Optional[float]
    min: Optional[float]
    max: Optional[float]
    sum: Optional[int]
    stddev: Optional[float]
    count: Optional[int]
    first: Optional[float]
    last: Optional[float]
    value: Optional[float]
    status: Optional[int]


class AggregateItemModel(TypedDict):
    id: str
    datapoints: List[AggregateModel]


class AggregateItemsModel(TypedDict):
    items: List[AggregateItemModel]


class GetAggregatesResponseModel(TypedDict):
    data: AggregateItemsModel
    count: Optional[int]
    continuationToken: Optional[str]


class TimeseriesModel(TypedDict):
    id: str
    name: str
    description: str
    step: bool
    unit: str
    createdTime: str
    changedTime: str
    assetId: str
    facility: str
    externalId: str
    source: str
    metadata: Optional[Dict[str, Any]]


class TimeseriesItemsModel(TypedDict):
    items: List[TimeseriesModel]


class GetTimeseriesResponseModel(TypedDict):
    data: TimeseriesItemsModel
    count: Optional[int]
    continuationToken: Optional[str]


class TimeseriesRequestItem(TypedDict, total=False):
    name: str
    description: Optional[str]
    step: Optional[bool]
    unit: Optional[str]
    assetId: Optional[str]
    facility: str
    externalId: Optional[str]
    metadata: Optional[Dict[str, Any]]


class TimeseriesPatchRequestItem(TypedDict, total=False):
    name: Optional[str]
    description: Optional[str]
    step: Optional[bool]
    unit: Optional[str]
    assetId: Optional[str]
    facility: Optional[str]
    externalId: Optional[str]
    metadata: Optional[Dict[str, Any]]


class FacilityModel(TypedDict):
    facility: str
    count: int


class FacilityItemsModel(TypedDict):
    items: List[FacilityModel]


class FacilityDataModel(TypedDict):
    data: FacilityItemsModel


class SourceModel(TypedDict):
    source: str
    count: int


class SourceItemsModel(TypedDict):
    items: List[SourceModel]


class SourceDataModel(TypedDict):
    data: SourceItemsModel


class HistoryItem(TypedDict):
    changedBy: str
    changedTime: str
    changes: Dict[str, dict]


class HistoryItemsModel(TypedDict):
    items: List[HistoryItem]


class GetHistoryResponseModel(TypedDict):
    data: HistoryItemsModel


class StreamSubscriptionRequestModel(TypedDict):
    id: str


class StreamSubscriptionModel(TypedDict):
    id: str
    customerId: str


class StreamSubscriptionItemsModel(TypedDict):
    items: List[StreamSubscriptionModel]


class StreamSubscriptionDataModel(TypedDict):
    data: StreamSubscriptionItemsModel


class TimeseriesRequestFailedException(Exception):
    def __init__(self, response: Response) -> None:
        try:
            error = json.loads(response.text)
        except:
            error = {
                "message": f"Could not load response, raw response: '{response.text}'"
            }
        self._status_code = response.status_code
        self._reason = response.reason
        self._message = error["message"]
        self._trace_id = error["traceId"] if "traceId" in error else None
        super().__init__(
            f"Status code: {self._status_code}, Reason: {self._reason}, Message: {self._message},  Trace ID: {self._trace_id}"
        )

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
