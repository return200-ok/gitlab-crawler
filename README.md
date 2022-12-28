# Gitlab-crawler
`Gitlab Crawler`  is a python job to get metrics of Gitlab Instance, collecting reporitory info and push to influxdb

## Install requirement <br>
```
pip install -r /path/to/requirements.txt
```
## Config env from .env <br>
Config your env like this
```
# influxdb
INFLUX_TOKEN = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ=="
INFLUX_DB = "http://192.168.3.101:8086"
INFLUX_ORG = "org"
BUCKET_NAME = "gitlab_test"
BEFORE_DAY = 30

# gitlab
GITLAB_URL = 'http://192.168.3.56:8098' 
GITLAB_PRIVATE_TOKEN = 'UJFWJWcxvWciPuQDugxu'

# config log
COLLECTOR_LOG_PATH = "logs/collector"
PRODUCER_LOG_PATH = "logs/producer"

# producer (days)
QUERY_TIME = 30
```
## Build docker image
```
#Build collecter
cd gitlab-crawler/collecter
docker build -t gitlab-crawler-collector:0.9 .
#Build producer
cd gitlab-crawler/producer
docker build -t gitlab-crawler-producer:0.9 .
```

## Start gitlab-crawler-collector
```
docker run -d \
-eINFLUX_TOKEN = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ==" \
-eINFLUX_DB = "http://192.168.3.101:8086" \
-eGITLAB_URL = 'http://192.168.3.56:8098' \
-eGITLAB_PRIVATE_TOKEN = 'UJFWJWcxvWciPuQDugxu' \
gitlab-crawler-collector:0.9
```
## Start gitlab-crawler-producer
```
docker run -d \
-eINFLUX_TOKEN = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ==" \
-eINFLUX_DB = "http://192.168.3.101:8086" \
-eGITLAB_URL = 'http://192.168.3.56:8098' \
-eGITLAB_PRIVATE_TOKEN = 'UJFWJWcxvWciPuQDugxu' \
gitlab-crawler-producer:0.9
```

### Change cronjob
Cronjob is set " 0 0 * * * " in current.
```
cat crontab
# START CRON JOB
0 0 * * * /usr/local/bin/python3 /gitlab-crawler-collector/main.py > /proc/1/fd/1 2>/proc/1/fd/2
# END CRON JOB
```

### Run with `docker compose`

#### Define your environment

Using the sample environment as a base, 

```bash
$ cd docker-compose
$ cp config/sample.env config/production.env
$ vim config/production.env
```
#### Start with docker compose 
To run with your newly configured environment, execute the following.

```bash
docker-compose up -d
```
### Viewing data with Grafana
By default, a grafana instance preloaded with templated dashboards will be started. Use your browser to view [http://localhost:3000](http://localhost:3000). The default username is `admin` and default password is `admin`. The dasboards are then accessible under the 'Home' tab.

### Templated Grafana dashboards

The files under `dashboards/*.json` contain a grafana dashboards described below.
Or you can import dashboard from [17718] ()

#### `Gitlab Analysis Dashboard` dashboard

The `Gitlab Analysis Dashboard` dashboard presents analysis data of reporitory from Gitlab. See an image of the dasboard with data below.
![overview!]()