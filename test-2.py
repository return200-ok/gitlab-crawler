import datetime

# print(datetime.datetime.strptime("2022-11-28T00:00:00+00:00", '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%SZ'))

# data = "2019-10-22T00:00:00.000-05:00"
data = "2022-11-28T00:00:00+00:00"
result1 = datetime.datetime.strptime(data[0:19],"%Y-%m-%dT%H:%M:%S")
# result2 = datetime.datetime.strptime(data[0:23],"%Y-%m-%dT%H:%M:%S.%f")
# result3 = datetime.datetime.strptime(data[0:9], "%Y-%m-%d")
# result4 = datetime.datetime.strptime(data[0:22], "%Y-%m-%dT%H:%M:%S.%f")
print(result1.strftime('%Y-%m-%dT%H:%M:%SZ'))