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


def test_retry_on_failure(api):
    with requests_mock.Mocker() as m:
        m.register_uri("GET", "https://test/1234/data/latest", status_code=503,  # 503 is retryable
                       text="""{"message": "Service is unavailable", "traceId": "1"}""")
        with pytest.raises(TimeseriesRequestFailedException):
            api.get_latest_datapoint("1234")
    assert m.call_count == 3, "Unexpected number of retries"


def test_skip_retry_when_not_retryable_status_code(api):
    with requests_mock.Mocker() as m:
        m.register_uri("GET", "https://test/1234/data/latest", status_code=403,  # 403 is not retryable
                       text="""{"message": "Service is unavailable", "traceId": "1"}""")
        with pytest.raises(TimeseriesRequestFailedException):
            api.get_latest_datapoint("1234")
    assert m.call_count == 1, "Unexpected number of retries"
