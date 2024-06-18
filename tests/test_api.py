import requests_mock
import pytest
from azure.identity._internal.msal_credentials import MsalCredential
from azure.core.credentials import AccessToken
from omnia_timeseries import TimeseriesAPI, TimeseriesEnvironment
from omnia_timeseries.http_client import TimeseriesRequestFailedException


class DummyCredentials(MsalCredential):

    def get_token(self, *scopes, **kwargs):
        return AccessToken("dummytoken", 0)

    def _get_app(self):
        return None


@pytest.fixture
def api():
    env = TimeseriesEnvironment("dummy", "https://test")
    api = TimeseriesAPI(DummyCredentials("dummy"), env)
    return api

def should_retry_request_when_failing_on_retryable_error_code_503_service_is_unavailable(api):
    with requests_mock.Mocker() as m:
        m.register_uri("GET", "https://test/1234/data/latest", status_code=503,
                       text="""{"message": "Service is unavailable", "traceId": "1"}""")
        with pytest.raises(TimeseriesRequestFailedException):
            api.get_latest_datapoint("1234")
    assert m.call_count == 3, "Unexpected number of retries"

def should_not_retry_request_when_failing_on_non_retryable_error_code_403_forbidden(api):
    with requests_mock.Mocker() as m:
        m.register_uri("GET", "https://test/1234/data/latest", status_code=403,
                       text="""{"message": "Service is unavailable", "traceId": "1"}""")
        with pytest.raises(TimeseriesRequestFailedException):
            api.get_latest_datapoint("1234")
    assert m.call_count == 1, "Unexpected number of retries"

def should_correctly_parse_empty_response_when_failing_on_502_bad_gateway_due_to_api_timeout(api):
    with requests_mock.Mocker() as m:
        m.register_uri("POST", "https://test/query/data", status_code=502, text="")

        with pytest.raises(TimeseriesRequestFailedException):
            api.get_multi_datapoints([
                {
                    "id": "some guid",
                    "statusFilter": [192],
                    "includeOutsidePoints": False,
                    "startTime": "2022-01-01T00:00:00.000Z",
                    "endTime": "2022-01-02T00:00:00.000Z",
                    "aggregateFunctions": ["avg"],
                    "processingInterval": "1h",
                    "fill": "none"
                },
            ])
    assert m.call_count == 3, "Unexpected number of retries"