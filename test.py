# data = {'commit_count': 5, 'storage_size': 220200, 'repository_size': 220200, 'lfs_objects_size': 0, 'job_artifacts_size': 0}
# print(data['commit_count'])
import datetime     # for general datetime object handling
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object
def get_date_object(date_string):
  return iso8601.parse_date(date_string)

def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)

print(get_date_string(datetime.datetime.now()))