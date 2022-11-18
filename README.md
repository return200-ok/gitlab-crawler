# Gitlab-collector
## Install requirement <br>
```
pip install -r /path/to/requirements.txt
```
## Config env from .env <br>
```
GITLAB_URL = 'http://192.168.3.56:8098' 
GITLAB_PRIVATE_TOKEN = 'UJFWJWcxvWciPuQDugxu'
INFLUX_TOKEN = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ=="
INFLUX_DB = "http://192.168.3.101:8086"
INFLUX_ORG = "org"
BUCKET_NAME = "gitlab"
BEFORE_DAY = 7
```
## Run collector to collect data from sonarqube and put them to influxdb
```
python3 gitlab-crawler.py
...
```
