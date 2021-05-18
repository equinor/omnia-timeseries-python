import unittest
import requests_mock
import pytest
from azure.identity._internal.msal_credentials import MsalCredential
from azure.core.credentials import AccessToken

from requests.models import Response
from omnia_timeseries import TimeseriesAPI, TimeseriesEnvironment
from omnia_timeseries.http_client import TimeseriesRequestFailedException

class DummyCredentials(MsalCredential):

    def get_token(self, *scopes, **kwargs):
        return AccessToken("dummytoken", 0)

    def _get_app(self):
        return None



class ApiTestCase(unittest.TestCase):

    def test_retry_on_failure(self):
        env = TimeseriesEnvironment("dummy", "https://test")
        api = TimeseriesAPI(DummyCredentials("dummy"), env)
        with requests_mock.Mocker() as m:
            m.register_uri("GET", "https://test/1234/data/latest", status_code=503, text="""{"message": "Service is unavailable", "traceId": "1"}""")
            with pytest.raises(TimeseriesRequestFailedException):
                response = api.get_latest_datapoint("1234")
        assert m.call_count == 3, "Unexpected number of retries"
            
