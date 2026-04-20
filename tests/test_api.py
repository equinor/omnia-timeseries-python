import requests_mock
import pytest
from azure.core.credentials import AccessToken
from omnia_timeseries import TimeseriesAPI, TimeseriesEnvironment
from omnia_timeseries.http_client import TimeseriesRequestFailedException

class DummyCredentials:
    def get_token(self, *scopes: str, **kwargs) -> AccessToken:
        return AccessToken("dummytoken", 0)


@pytest.fixture
def api():
    env = TimeseriesEnvironment.Dev()
    api = TimeseriesAPI(azure_credential=DummyCredentials(), environment=env)
    api._base_url = "https://test"
    return api


def should_retry_request_when_failing_on_retryable_error_code_503_service_is_unavailable(
    api,
):
    with requests_mock.Mocker() as m:
        m.register_uri(
            "GET",
            "https://test/1234/data/latest",
            status_code=503,
            text="""{"message": "Service is unavailable", "traceId": "1"}""",
        )
        with pytest.raises(TimeseriesRequestFailedException):
            api.get_latest_datapoint("1234")
    assert m.call_count == 3, "Unexpected number of retries"


def should_not_retry_request_when_failing_on_non_retryable_error_code_403_forbidden(
    api,
):
    with requests_mock.Mocker() as m:
        m.register_uri(
            "GET",
            "https://test/1234/data/latest",
            status_code=403,
            text="""{"message": "Service is unavailable", "traceId": "1"}""",
        )
        with pytest.raises(TimeseriesRequestFailedException):
            api.get_latest_datapoint("1234")
    assert m.call_count == 1, "Unexpected number of retries"


@pytest.mark.parametrize("responseText", [(""), ("blah")])
def should_try_parse_response_when_failing_on_502_bad_gateway_due_to_api_timeout(
    api, responseText
):
    with requests_mock.Mocker() as m:
        m.register_uri(
            "POST", "https://test/query/data", status_code=502, text=responseText
        )

        with pytest.raises(TimeseriesRequestFailedException):
            api.get_multi_datapoints(
                [
                    {
                        "id": "some guid",
                        "statusFilter": [192],
                        "includeOutsidePoints": False,
                        "startTime": "2022-01-01T00:00:00.000Z",
                        "endTime": "2022-01-02T00:00:00.000Z",
                        "aggregateFunctions": ["avg"],
                        "processingInterval": "1h",
                        "fill": "none",
                    },
                ]
            )
    assert m.call_count == 3, "Unexpected number of retries"


def should_forward_align_to_cache_parameter_for_multi_datapoints(api):
    with requests_mock.Mocker() as m:
        m.register_uri(
            "POST",
            "https://test/query/data",
            json={"data": {"items": []}},
        )
        api.get_multi_datapoints([{"id": "series-1"}], alignToCache=True)
        assert m.call_count == 1, "Expected a single request"
        request = m.request_history[0]
        assert request.qs.get("aligntocache") == [
            "true"
        ], "alignToCache should be forwarded"


def should_forward_align_to_cache_parameter_for_get_aggregates(api):
    with requests_mock.Mocker() as m:
        m.register_uri(
            "GET",
            "https://test/1234/data/aggregates",
            json={"data": {"items": []}},
        )
        api.get_aggregates("1234", ["avg"], alignToCache=False)
        assert m.call_count == 1, "Expected a single request"
        request = m.request_history[0]
        assert request.qs.get("aligntocache") == [
            "false"
        ], "alignToCache should be forwarded as false"


def should_include_debug_query_param_when_debug_mode_is_enabled(api):
    api._debug_mode = True
    with requests_mock.Mocker() as m:
        m.register_uri(
            "POST",
            "https://test/query/data",
            json={"data": {"items": []}},
        )
        api.get_multi_datapoints([{"id": "series-1"}])
        assert m.call_count == 1, "Expected a single request"
        request = m.request_history[0]
        assert request.qs.get("debug") == [
            "true"
        ], "Debug mode should inject debug=true"
