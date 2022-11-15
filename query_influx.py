import os
from os import environ
from time import time
import json
import logging
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
import gitlab
gl = gitlab.Gitlab(url='http://192.168.3.56:8098', private_token='UJFWJWcxvWciPuQDugxu')
influx_token = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ=="
influx_server = "http://192.168.3.101:8086"
org_name = "org"
bucket_name = "gitlab"

with InfluxDBClient(url=influx_server, token=influx_token, org=org_name) as client:
    query_api = client.query_api()
    query = ' from(bucket: "gitlab")\
    |> range(start: -24h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "1")\
    |> filter(fn: (r) => r["_field"] == "commit_id") '
    result = query_api.query(org=org_name, query=query)
    json_data = []
    for table in result:
        for record in table.records:
            json_data.append({
                "measurement": record.get_measurement(),
                "fields":{
                    "tag": record.get_field(),
                    "value": record.get_value()
                },
                "time": record.get_time() # can be shaped as you like, e.g. ISO with .replace(tzinfo=None).isoformat()+'Z'
            })
            print(json_data[0])
