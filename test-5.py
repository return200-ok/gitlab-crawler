query = '''import "date"\
from(bucket: "gitlab_test")\
  |> range(start: -30d, stop: now())\
  |> filter(fn: (r) => r["_measurement"] == "commit")\
  |> filter(fn: (r) => r["_field"] == "commit_id")\
  |> filter(fn: (r) => r["project_id"] == "{id}")\
  |> truncateTimeColumn(unit: 1d)\
  |> group(columns: ["project_id", "_time"], mode:"by")\
  |> count()'''
print(query.format(id=5))    
