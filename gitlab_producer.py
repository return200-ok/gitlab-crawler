import datetime as dt
import logging
import os
import sys
from datetime import datetime, timedelta
from os import environ
from time import time

import rfc3339
from datetime_truncate import truncate
from dotenv import load_dotenv
from influx_client import InfluxClient
from query_client import InfluxQueryClient

import gitlab

'''
  Load env
'''
load_dotenv()
gl = gitlab.Gitlab(url=os.getenv('GITLAB_URL'), private_token=os.getenv('GITLAB_PRIVATE_TOKEN'))
influx_token = os.getenv('INFLUX_TOKEN')
influx_server = os.getenv('INFLUX_DB')
org_name = os.getenv('INFLUX_ORG')
bucket_name = os.getenv('BUCKET_NAME')
before_day = float(os.getenv('BEFORE_DAY'))
logPath = os.getenv('PRODUCER_LOG_PATH')
query_time = int(os.getenv('QUERY_TIME'))

'''
  Config logging handler
'''
def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)

duration_time = datetime.now() - timedelta(before_day)
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
fileName = get_date_string(datetime.now())+'_gitlab_producer'
fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logFormatter)

'''
  Avoid duplicated logs
'''
if (rootLogger.hasHandlers()):
    rootLogger.handlers.clear()
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
logging.getLogger().setLevel(logging.DEBUG)

'''
  Query to get list project
'''
query_project = 'from(bucket: "gitlab_test")\
  |> range(start: -30d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "project")'

query_client = InfluxQueryClient(influx_server, influx_token, org_name, bucket_name, "")
write_client = InfluxClient(influx_server, influx_token, org_name, bucket_name)

'''
  Get list project
'''
result = query_client.query_to_json(query_project)
project_list = []
for i in range(0, len(result)):
  entries_to_remove = ('result', 'table')
  for k in entries_to_remove:
    result[i].pop(k, None)
  project_id = result[i]['_value']
  project_list.append(project_id)
project_list = set(project_list)

'''
  Get list of day if result has value
'''
def get_value_by_day(time, result):
    res = None
    for sub in result:
        res_time = sub['_time']
        res_time = dt.datetime.strptime(res_time[0:19],"%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')
        if res_time == time:
            res = sub
            return res

'''
  Get time range to consumming data
'''
today = truncate(datetime.today(), 'day')
time_range = []
for day in range(0,(query_time-1)): 
    d = today - timedelta(days=day)
    
    '''
      Convert time to rfc339 format
    '''
    time_range.append(d.strftime('%Y-%m-%dT%H:%M:%SZ'))

'''
  Producing data 
'''
def producer_data(query, measurement):
  for project in project_list:
    
    '''
      Generate query with project ID
    '''
    q = query.format(id=project)
    res = query_client.query_to_json(q)

    days_has_value = []
    for i in range(0, len(res)):
        time = res[i]['_time']        
        '''
          Convert time to rfc339 format
        '''
        time = dt.datetime.strptime(time[0:19],"%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')
        days_has_value.append(time)

    for t in time_range:        
        '''
          Default value = 0
        '''
        value = 0
        
        '''
          If days has a value then get value from result
        '''
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

        '''
          Write record to bucket
        '''
        try:
            write_client.write_data(record)
            logging.info("Wrote "+str(record)+" to bucket "+bucket_name)
        except Exception as e:
            logging.error("Problem inserting points for current batch")
            raise e
if __name__ == '__main__':

  '''
    Start process
  '''
  start_time = datetime.now()

  def consum_commit():

    '''
      Query to count commit of a project each day
    '''
    query_commit = '''import "date"\
    from(bucket: "gitlab_test")\
      |> range(start: -30d, stop: now())\
      |> filter(fn: (r) => r["_measurement"] == "commit")\
      |> filter(fn: (r) => r["project_id"] == "{id}")\
      |> filter(fn: (r) => r["_field"] == "commit_id")\
      |> truncateTimeColumn(unit: 1d)\
      |> group(columns: ["project_id", "_time"], mode:"by")\
      |> count()'''
    producer_data(query_commit, "commit_total")

  def consum_issue():

    '''
      Query to count issue of a project each day
    '''
    query_issue = '''import "date"\
    from(bucket: "gitlab_test")\
      |> range(start: -30d, stop: now())\
      |> filter(fn: (r) => r["_measurement"] == "issue")\
      |> filter(fn: (r) => r["project_id"] == "{id}")\
      |> filter(fn: (r) => r["_field"] == "issue_id")\
      |> truncateTimeColumn(unit: 1d)\
      |> group(columns: ["project_id", "_time"], mode:"by")\
      |> count()'''
    producer_data(query_issue, "issue_total")

  def consum_mrs():

    '''
      Query to count merge request of a project each day
    '''
    query_mrs = '''import "date"\
    from(bucket: "gitlab_test")\
      |> range(start: -30d, stop: now())\
      |> filter(fn: (r) => r["_measurement"] == "mrs")\
      |> filter(fn: (r) => r["project_id"] == "{id}")\
      |> filter(fn: (r) => r["_field"] == "mrs_id")\
      |> truncateTimeColumn(unit: 1d)\
      |> group(columns: ["project_id", "_time"], mode:"by")\
      |> count()'''
    producer_data(query_mrs, "mrs_total")
  
  consum_commit()
  consum_issue()
  consum_mrs()

  print()
  logging.info(f'Import data finished in: {datetime.now() - start_time}')
  print()
  write_client.close_process()
