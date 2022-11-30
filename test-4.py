
import datetime as dt
import json
from datetime import date, datetime, timedelta

from datetime_truncate import truncate
from influx_client import InfluxClient
from influxdb_client.client.write_api import SYNCHRONOUS
from query_client import InfluxQueryClient

result_1 = [
    {'_time': '2022-11-09T00:00:00Z', 'project_id': '1', '_value': 2}, 
    {'_time': '2022-11-22T00:00:00Z', 'project_id': '1', '_value': 1}]

result = [
    {'_time': '2022-11-09T00:00:00+00:00', 'project_id': '1', '_value': 2}, 
    {'_time': '2022-11-22T00:00:00+00:00', 'project_id': '1', '_value': 1}]

def get_value_by_day(time):
    res = None
    for sub in result:
        res_time = sub['_time']
        res_time = dt.datetime.strptime(res_time[0:19],"%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')
        if res_time == time:
            res = sub
            return res

days_has_value = []
for i in range(0, len(result)):
    time = result[i]['_time']
    time = dt.datetime.strptime(time[0:19],"%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')
    days_has_value.append(time)

today = truncate(datetime.today(), 'day')
time_range = []
for day in range(0,29): 
    d = today - timedelta(days=day)
    time_range.append(d.strftime('%Y-%m-%dT%H:%M:%SZ'))
for t in time_range:
    value = 0
    if t in days_has_value:
        r = get_value_by_day(t)
        value = r['_value']
    print(t, value)
