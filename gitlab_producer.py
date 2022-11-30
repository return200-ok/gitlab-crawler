import datetime as dt
import json
from datetime import date, datetime, timedelta

from datetime_truncate import truncate
from influx_client import InfluxClient
from influxdb_client.client.write_api import SYNCHRONOUS
from query_client import InfluxQueryClient

influx_token = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ=="
influx_server = "http://192.168.3.101:8086"
org_name = "org"
bucket_name = "gitlab_test"


query_commit = '''import "date"\
from(bucket: "gitlab_test")\
  |> range(start: -30d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "commit")\
  |> filter(fn: (r) => r["project_id"] == "{id}")\
  |> filter(fn: (r) => r["_field"] == "commit_id")\
  |> truncateTimeColumn(unit: 1d)\
  |> group(columns: ["project_id", "_time"], mode:"by")\
  |> count()'''
query_issue = '''import "date"\
from(bucket: "gitlab_test")\
  |> range(start: -30d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "issue")\
  |> filter(fn: (r) => r["project_id"] == "{id}")\
  |> filter(fn: (r) => r["_field"] == "issue_id")\
  |> truncateTimeColumn(unit: 1d)\
  |> group(columns: ["project_id", "_time"], mode:"by")\
  |> count()'''
query_mrs = '''import "date"\
from(bucket: "gitlab_test")\
  |> range(start: -30d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "mrs")\
  |> filter(fn: (r) => r["project_id"] == "{id}")\
  |> filter(fn: (r) => r["_field"] == "mrs_id")\
  |> truncateTimeColumn(unit: 1d)\
  |> group(columns: ["project_id", "_time"], mode:"by")\
  |> count()'''
query_project = 'from(bucket: "gitlab_test")\
  |> range(start: -30d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "project")'

query_client = InfluxQueryClient(influx_server, influx_token, org_name, bucket_name, query_commit)

result = query_client.query_to_json(query_project)
project_list = []
for i in range(0, len(result)):
  entries_to_remove = ('result', 'table')
  for k in entries_to_remove:
    result[i].pop(k, None)
  project_id = result[i]['_value']
  project_list.append(project_id)
project_list = set(project_list)

def get_value_by_day(time, result):
    res = None
    for sub in result:
        res_time = sub['_time']
        res_time = dt.datetime.strptime(res_time[0:19],"%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')
        if res_time == time:
            res = sub
            return res

today = truncate(datetime.today(), 'day')
time_range = []
for day in range(0,29): 
    d = today - timedelta(days=day)
    time_range.append(d.strftime('%Y-%m-%dT%H:%M:%SZ'))

def producer_data(query, measurement):
  for project in project_list:
    q = query.format(id=project)
    res = query_client.query_to_json(q)

    days_has_value = []
    for i in range(0, len(res)):
        time = res[i]['_time']
        time = dt.datetime.strptime(time[0:19],"%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')
        days_has_value.append(time)

    for t in time_range:
        value = 0
        if t in days_has_value:
            r = get_value_by_day(t, res)
            value = r['_value']
        record = [{
            "measurement": measurement,
            "tags": {
                "project_id": project,
            },
            "time": t,
            "fields": {
                "value": value,
            }
        }]
        print(record)
        # client.write_data(record)

if __name__ == '__main__':
  producer_data(query_commit, "commit_total")
  producer_data(query_issue, "issue_total")
  producer_data(query_mrs, "mrs_total")
      

