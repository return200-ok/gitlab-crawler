import json
import rfc3339
from influxdb_client import Dialect, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

influx_token = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ=="
influx_server = "http://192.168.3.101:8086"
org_name = "org"
bucket_name = "gitlab_test"
query = 'from(bucket: "test")\
  |> range(start: -14d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "commit")\
  |> unique(column: "_value")\
  |> keep(columns: ["gitlab_project_id", "_field", "_value"])'
queryA = 'from(bucket: "test")\
  |> range(start: -14d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "commit")'
queryB = 'import "date"\
from(bucket: "gitlab_test")\
  |> range(start: -14d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "commit")\
  |> filter(fn: (r) => r["_field"] == "commit_id")\
  |> unique(column: "key")\
  |> filter(fn: (r) => r["_time"] < date.sub(d: 24h, from: now()))\
  |> group()  \
  |> count()'
queryC = 'from(bucket: "gitlab_test")\
  |> range(start: -14d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "commit")\
  |> filter(fn: (r) => r["_field"] == "commit_id")'
queryD = 'import "date"\
from(bucket: "gitlab_test")\
  |> range(start: date.truncate(t: -14d, unit: 1d))\
  |> filter(fn: (r) => r["_measurement"] == "commit")\
  |> filter(fn: (r) => r["_field"] == "commit_id")\
  |> group(columns: ["key", "_time"], mode:"by")\
  |> count()'
queryE = 'import "date"\
from(bucket: "gitlab_test")\
  |> range(start: -14d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "commit")\
  |> filter(fn: (r) => r["project_id"] == "2")\
  |> filter(fn: (r) => r["_field"] == "commit_id")\
  |> truncateTimeColumn(unit: 1d)\
  |> group(columns: ["project_id", "_time"], mode:"by")\
  |> count()'

with InfluxDBClient(url=influx_server, token=influx_token, org=org_name) as client:

    '''
    query to csv full
    '''
    # # Query: using CSV iterator
    # csv_iterator = client.query_api().query_csv(query)

    # # Serialize to values
    # output = csv_iterator.to_values()
    # print(output)

    '''
    query to csv
    '''
    # # Query: using CSV iterator
    # csv_iterator = client.query_api().query_csv(query,
    #                                             dialect=Dialect(header=False, annotations=[]))

    # for csv_line in csv_iterator:
    #     print(csv_line)

    '''
    query to JSON
    '''
    # Query: using Table structure
    tables = client.query_api().query(queryE)

    # Serialize to JSON
    output = tables.to_json(indent=5)

    # Convert date object to string in rfc3339
    def get_date_string(date_object):
      return rfc3339.rfc3339(date_object)
    # Convert output to JSON
    x = json.loads(output)
    for i in range(0, len(x)):
      entries_to_remove = ('result', 'table')
      for k in entries_to_remove:
        x[i].pop(k, None)
      # print(x[i]['_time'])
      project_id = x[i]['project_id']
      time = x[i]['_time']
      value = x[i]['_value']

      commit_total = [{
          "measurement": "commit_total",
          "tags": {
              "project_id": project_id,
          },
          "time": time,
          "fields": {
              "value": value,
          }
      }]
      print(commit_total)

      client.write_api(write_options=SYNCHRONOUS).write(bucket_name, org_name, commit_total)

    '''
    query to column
    '''
    # # Query: using Table structure
    # tables = client.query_api().query(queryE)

    # # Serialize to values
    # output = tables.to_values(columns=['project_id', '_time', '_value'])
    # print(output)
    

    # print(get_date_string(output[0][0]))

    # for i in range(0, 1):
    #   commit_total = [{
    #       "measurement": "commit_total",
    #       "tags": {
    #           "project_id": output[i][0],
    #       },
    #       "time": get_date_string(output[i][1]),
    #       "fields": {
    #           "value": output[i][2],
    #       }
    #   }]
    #   print(commit_total)

    # client.write_api(write_options=SYNCHRONOUS).write(bucket_name, org_name, commit_total)