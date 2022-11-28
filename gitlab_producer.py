import json

from influx_client import InfluxClient
from influxdb_client.client.write_api import SYNCHRONOUS
from query_client import InfluxQueryClient

influx_token = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ=="
influx_server = "http://192.168.3.101:8086"
org_name = "org"
bucket_name = "gitlab_test"

query_commit = 'import "date"\
from(bucket: "gitlab_test")\
  |> range(start: -30d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "commit")\
  |> filter(fn: (r) => r["_field"] == "commit_id")\
  |> truncateTimeColumn(unit: 1d)\
  |> group(columns: ["project_id", "_time"], mode:"by")\
  |> count()'
query_issue = 'import "date"\
from(bucket: "gitlab_test")\
  |> range(start: -30d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "issue")\
  |> filter(fn: (r) => r["_field"] == "issue_id")\
  |> truncateTimeColumn(unit: 1d)\
  |> group(columns: ["project_id", "_time"], mode:"by")\
  |> count()'
query_mrs = 'import "date"\
from(bucket: "gitlab_test")\
  |> range(start: -30d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "mrs")\
  |> filter(fn: (r) => r["_field"] == "mrs_id")\
  |> truncateTimeColumn(unit: 1d)\
  |> group(columns: ["project_id", "_time"], mode:"by")\
  |> count()'

def producer_data(query, measurement):
  result = query_client.query_to_json(query)
  for i in range(0, len(result)):
    entries_to_remove = ('result', 'table')
    for k in entries_to_remove:
      result[i].pop(k, None)
    project_id = result[i]['project_id']
    time = result[i]['_time']
    value = result[i]['_value']
    record = [{
        "measurement": measurement,
        "tags": {
            "project_id": project_id,
        },
        "time": time,
        "fields": {
            "value": value,
        }
    }]
    # print(record)
    client = InfluxClient(influx_server, influx_token, org_name, "gitlab_test")
    client.write_data(record)


if __name__ == '__main__':
    query_client = InfluxQueryClient(influx_server, influx_token, org_name, bucket_name, query_commit)
    producer_data(query_commit, "commit_total")
    producer_data(query_issue, "issue_total")
    producer_data(query_mrs, "mrs_total")
