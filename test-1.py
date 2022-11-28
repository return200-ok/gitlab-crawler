from influxdb_client import InfluxDBClient

influx_token = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ=="
influx_server = "http://192.168.3.101:8086"
org_name = "org"
bucket_name = "gitlab"
client = InfluxDBClient(influx_server, influx_token, org_name)
query = 'from(bucket: "test")\
  |> range(start: -14d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "commit")'


import json
from influxdb_client.client.flux_table import FluxStructureEncoder
list_result = client.query_api().query(org=org_name, query=query)
output = json.dumps(list_result, cls=FluxStructureEncoder, indent=2)
print(output[0])

# def count_commit_per_day(query):
#     client.check_query(query)
#     list_result = client.query_response_to_json(query)
#     return list_result
# print(count_commit_per_day(query))
# list_result = client.query_response_to_json(query)
# list_result = client.query_api().query(org=org_name, query=query)

# Serialize to values
# output = list_result.to_values(columns=['_measurement', '_time', '_value', 'gitlab_project_id'])
# print(output)

# Serialize to JSON
# output = list_result.to_json(indent=5)
# print(output[0])
# for i in output:
  # client.write_api().write(bucket_name, org_name, i)
  # print(i)

# results = []
# for table in list_result:
#     for record in table.records:
#         # results.append((record.get_value(), record.get_field()))
#         results.append((record.values))
# print(results)



# print(list_result)

# def query_flux(unit, unique_id,
#                value=None, measure=None, channel=None, ts_str=None,
#                start_str=None, end_str=None, past_sec=None, group_sec=None,
#                limit=None):
#     """Generate influxdb query string (flux edition, using influxdb_client)."""
#     from influxdb_client import InfluxDBClient

#     settings = db_retrieve_table_daemon(Misc, entry='first')
#     influxdb_url = f'http://{settings.measurement_db_host}:{settings.measurement_db_port}'

#     client = InfluxDBClient(
#         url=influxdb_url,
#         username=settings.measurement_db_user,
#         password=settings.measurement_db_password,
#         org='mycodo',
#         timeout=5000)
#     query_api = client.query_api()

#     query = f'from(bucket: \"{settings.measurement_db_dbname}\")'

#     if past_sec:
#         query += f' |> range(start: -{past_sec}s)'
#     elif start_str and end_str:
#         query += f' |> range(start: {start_str}, stop: {end_str})'
#     elif start_str:
#         query += f' |> range(start: {start_str})'
#     elif end_str:
#         query += f' |> range(stop: {end_str})'
#     else:
#         query += f' |> range(start: -99999d)'

#     query += f' |> filter(fn: (r) => r["_measurement"] == "{unit}")'
#     query += f' |> filter(fn: (r) => r["device_id"] == "{unique_id}")'

#     if channel is not None:
#         query += f' |> filter(fn: (r) => r["channel"] == "{channel}")'
#     if measure:
#         query += f' |> filter(fn: (r) => r["measure"] == "{measure}")'
#     if ts_str:
#         query += " AND time = '{ts}'".format(ts=ts_str)

#     if group_sec:
#         query += f' |> aggregateWindow(every: {group_sec}s, fn: mean)'
#     if limit:
#         query += f' |> limit(n:{limit})'

#     if value:  # value is deprecated. Use function instead.
#         if value == "LAST":
#             query += ' |> last()'
#         elif value == "FIRST":
#             query += ' |> first()'
#         elif value == "MAX":
#             query += ' |> max()'
#         elif value == "MIN":
#             query += ' |> min()'
#         elif value == "COUNT":
#             query += ' |> count()'

#         # bug in influxdb 1.8: Error: panic: runtime error: invalid memory address or nil pointer dereference
#         # fix this when moving from influxdb 1.8 to 2.x
#         elif value == "SUM":
#             query += ' |> sum(column: "_value")'
#         elif value == "MEAN":
#             query += ' |> mean()'

#         else:
#             logger.error(f"query_flux(): Unknown value: '{value}'")
#             return 1

#     logger.debug(f"query_flux() query: '{query}'")

#     tables = query_api.query(query)

#     return tables

