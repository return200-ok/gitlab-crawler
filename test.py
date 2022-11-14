import datetime     # for general datetime object handling
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object
from datetime import datetime, timedelta

def get_date_object(date_string):
  return iso8601.parse_date(date_string)

def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)

input_string = '2022-11-09T09:56:00.691Z'
test_date = get_date_object(input_string)
# print(type(input_string))
yesterday = datetime.now() - timedelta(days = 1)
print(get_date_string(yesterday))