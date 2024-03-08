from omnia_timeseries.api import TimeseriesAPI, TimeseriesEnvironment
import pandas as pd

api = TimeseriesAPI(environment=TimeseriesEnvironment.Prod())
ts_ifm = api.get_timeseries(facility="SNA", source="IFM")
try:
    api = TimeseriesAPI()
    ts_ifm_2 = api.get_timeseries(facility="SNA", source="IFM")

    # ts_ims = api.get_timeseries(facility="SNA", source="IMS")

    tags = ts_ifm["data"]["items"]
    # tags = ts_ifm["data"]["items"]

    df = pd.DataFrame(tags)

    print(df.head)
    for k in range(0, len(df.index)-1):
        try:
            point_id = df.loc[k, "id"]
            ts2 = api.get_timeseries_by_id(id=point_id)
            # print(ts2)

            actual_points = api.get_datapoints(
                id=point_id, startTime="2021-11-01T09:45:10+00:00", endTime="2021-11-15T09:45:10+00:00")
            print(actual_points)

            last_point = api.get_latest_datapoint(id=point_id)
            print(last_point)
            first_point = api.get_first_datapoint(id=point_id)
            print(first_point)
        except Exception as ex:
            pass
except Exception as ex:
    print(ex)