import datetime as dt
from datetime import date, datetime, timedelta

import rfc3339
from datetime_truncate import truncate

# days_to_subtract = 1

today = truncate(datetime.today(), 'day')
# d = today - timedelta(days=days_to_subtract)

# def get_date_string(date_object):
#   return rfc3339.rfc3339(date_object)
# print(get_date_string(d))

time = "2022-11-28T00:00:00+00:00"
time = dt.datetime.strptime(time[0:19],"%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')

for i in range(0,29):
  d = today - timedelta(days=i)
  # print(get_date_string(d))
  time_range = []
  time_range.append(d.strftime('%Y-%m-%dT%H:%M:%SZ'))
  # print(time_range)
  for t in time_range:
    if t == time:
      print(t)



    # start_time = "2022-09-10T08:26:51.098Z" # type string: timestamp rfc3339
    # stop_time = "2022-11-25T00:00:00.098Z"
    # for measurement in ['branch']:
    #     client.delete_data(start_time, stop_time, measurement)

    # projects = get_projects()
    # print(get_branches(projects[0])[0])

    # data_point = [{
    #     "measurement": "branch",
    #     "tags": {
    #         "project_name": "influx",
    #         "project_id": "686",
    #     },
    #     "fields": {
            
    #         "branch_name": "master",
    #         "branch_name": "develop",
    #         "branch_name": "feature"
    #     }
    # }]
    # client.write_data(data_point)