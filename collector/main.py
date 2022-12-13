import logging
import os
import sys
from datetime import datetime, timedelta
from os import environ
from time import time

import rfc3339
from dotenv import load_dotenv
from influxdb_client.client.write_api import ASYNCHRONOUS
from lib.influx_client import InfluxClient, InfluxPoint

import gitlab

'''
    Load env
'''
load_dotenv()
gitlab_url = os.getenv('GITLAB_URL')
gitlab_token = os.getenv('GITLAB_PRIVATE_TOKEN')
gl = gitlab.Gitlab(url=gitlab_url, private_token=gitlab_token)
influx_token = os.getenv('INFLUX_TOKEN')
influx_server = os.getenv('INFLUX_DB')
org_name = os.getenv('INFLUX_ORG')
bucket_name = os.getenv('BUCKET_NAME')
before_day = float(os.getenv('BEFORE_DAY'))
logPath = os.getenv('COLLECTOR_LOG_PATH')

'''
Config logging handler
'''
def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)

duration_time = datetime.now() - timedelta(before_day)
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
fileName = get_date_string(datetime.now())+'_gitlab_collecter'
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
    Get list projects
    UserWarning: Calling a `list()` method without specifying `get_all=True` or `iterator=True` 
    will return a maximum of 20 items. Your query returned 20 of many items. 
    See https://python-gitlab.readthedocs.io/en/v3.11.0/api-usage.html#pagination for more details. 
'''
def get_projects():
    projects = gl.projects.list(get_all=True)
    return projects

'''
    Get project statics    
'''
def get_project_size(project):
    project_id = project.id
    project_size = gl.projects.get(id=project_id,statistics=True)
    return project_size

'''
    Get the list of branches for a repository
'''
def get_branches(project):
    branches = project.branches.list(created_after=duration_time)
    return branches

'''
    List the commits for a project
'''
def get_commits(project):
    commits = project.commits.list(created_after=duration_time)
    return commits

'''
    List the project issues
'''
def get_issues(project):
    issues = project.issues.list(created_after=duration_time)
    return issues

'''
    List MRs/Pull-request for a project
'''
def get_mrs(project):
    mrs = project.mergerequests.list(created_after=duration_time)
    return mrs

class Stats:
    def __init__(self, statistics):
        self.statistics = statistics

'''
    Create Commits object
'''
class Commits:
    def __init__(self, id, short_id, title, created_at, author_email):
        self.id = id
        self.short_id = short_id
        self.title = title
        self.created_at = created_at
        self.author_email = author_email
  
'''
    reate Issues object
'''
class Issues:
    def __init__(self, id, project_id, title, state, created_at, updated_at):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.state = state
        self.created_at = created_at
        self.updated_at = updated_at  

'''
    Create MRs/Pull-request object
'''
class Mrs:
    def __init__(self, id, project_id, title, state, created_at, updated_at, target_branch, source_branch):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.state = state
        self.created_at = created_at
        self.updated_at = updated_at  
        self.target_branch = target_branch
        self.source_branch = source_branch

''' 
    Gen data point
'''
def gen_datapoint(kpi_type, kpi_data, i):
    if kpi_type == "project":
        measurement = kpi_type
        tags = {
            "project_name": kpi_data[i].name,
            }
        fields = {
            "project_id": kpi_data[i].id,
            }
        data_point = InfluxPoint(measurement, tags, fields)._point
        return data_point
    elif kpi_type == "branch":
        measurement = kpi_type
        tags = {
            "project_id": project.id,
            "project_name": project.name,
            "key": str(project.id)+"_"+str(kpi_data[i].name),
            }
        fields = {
            "branch": kpi_data[i].name,
            }
        data_point = InfluxPoint(measurement, tags, fields)._point
        return data_point
    elif kpi_type == "mrs":
        data = Mrs(kpi_data[i].id, kpi_data[i].project_id, kpi_data[i].title, kpi_data[i].state, kpi_data[i].created_at, kpi_data[i].updated_at, kpi_data[i].target_branch, kpi_data[i].source_branch)
        measurement = kpi_type
        tags = {
            "project_id": project.id,
            "project_name": project.name,
            "target_branch": data.target_branch,
            "source_branch": data.source_branch,
            "key": str(project.id)+"_"+str(data.id),
            }
        timestamp = data.created_at
        fields = {
            "mrs_id": data.id,
            "mrs_title": data.title,
            "state": data.state,
            }
        data_point = InfluxPoint(measurement, tags, fields, timestamp)._point
        return data_point
    elif kpi_type == "issue":
        data = Issues(kpi_data[i].id, kpi_data[i].project_id, kpi_data[i].title, kpi_data[i].state, kpi_data[i].created_at, kpi_data[i].updated_at)
        measurement = kpi_type
        tags = {
            "project_id": project.id,
            "project_name": project.name,
            "key": str(project.id)+"_"+str(data.id)
            }
        timestamp = data.created_at
        fields = {
            "issue_id": data.id,
            "issue_title": data.title,
            "issue_state": data.state,
            }
        data_point = InfluxPoint(measurement, tags, fields, timestamp)._point
        return data_point
    elif kpi_type == "commit":
        data = Commits(kpi_data[i].id, kpi_data[i].short_id, kpi_data[i].title, kpi_data[i].created_at, kpi_data[i].author_email)
        measurement = kpi_type
        tags = {
            "project_id": project.id,
            "project_name": project.name,
            "author_email": data.author_email,
            "key": str(project.id)+"_"+str(data.short_id)
            }
        timestamp = data.created_at
        fields = {
            "commit_id": data.short_id,
            "commit_title": data.title,
            }
        data_point = InfluxPoint(measurement, tags, fields, timestamp)._point
        return data_point
    elif kpi_type == "statistics":
        data = Stats(kpi_data[i].statistics)
        measurement = kpi_type
        tags = {
            "project_id": project.id,
            "project_name": project.name,
            # "key": (project.id)+"_"+(data.id)
        }
        timestamp = int(time())
        fields = {
            "storage_size": data.statistics['storage_size'],
            "repository_size": data.statistics['repository_size'],
            "lfs_objects_size": data.statistics['lfs_objects_size'],
            "job_artifacts_size": data.statistics['job_artifacts_size'],
            }
        data_point = InfluxPoint(measurement, tags, fields, timestamp)._point
        return data_point
    else:
        logging.warning("kpi_type is not matching!")

'''
    Pushing data to bucket
'''
def push_data(kpi, data):
    if len(data) > 0:
        for i in range(0, len(data)):
            data_point = gen_datapoint(kpi, data, i)
            try:
                client.write_data(data_point)
                logging.info("Wrote "+str(data_point)+" to bucket "+bucket_name)
            except Exception as e:
                logging.error("Problem inserting points for current batch")
                raise e

if __name__ == '__main__':

    client = InfluxClient(influx_server, influx_token, org_name, "gitlab_test")

    '''
    Check connection & write
    '''
    client.check_connection()
    client.check_write()

    '''
    Start process
    '''
    start_time = datetime.now()

    '''
    Get list project & kpis
    '''
    projects = get_projects()
    push_data("project", projects)

    '''
    List kpi to collecting
    '''
    kpis = ["project", "branch", "mrs", "issue", "commit", "statistics"]

    for kpi in kpis:
        if kpi == "branch":
            for project in projects:
                branch = get_branches(project)
                push_data(kpi, branch)
        elif kpi == "mrs":
            for project in projects:
                mrs = get_mrs(project)
                push_data(kpi, mrs)
        elif kpi == "issue":
            for project in projects:
                issue = get_issues(project)
                push_data(kpi, issue)
        elif kpi == "commit":
            for project in projects:
                commit = get_commits(project)
                push_data(kpi, commit)
        elif kpi == "statistics":
            for project in projects:
                statistics = []
                statistics.append(get_project_size(project))
                push_data(kpi, statistics)

    print()
    logging.info(f'Import finished in: {datetime.now() - start_time}')
    print()
    client.close_process()