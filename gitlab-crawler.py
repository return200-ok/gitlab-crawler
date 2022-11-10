import os
from os import environ
from time import time
import json
import requests
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
import gitlab
gl = gitlab.Gitlab(url='http://192.168.3.56:8098', private_token='UJFWJWcxvWciPuQDugxu')
influx_token = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ=="
influx_server = "http://192.168.3.101:8086"
org_name = "org"
bucket_name = "gitlab"


#List projects
def get_projects():
    projects = gl.projects.list()
    return projects

#Get the list of branches for a repository
def get_branches(project):
    branches = project.branches.list()
    return branches

#List the commits for a project
def get_commits(project):
    commits = project.commits.list()
    return commits

#List the project issues
def get_issues(project):
    issues = project.issues.list()
    return issues

#List MRs/Pull-request for a project
def get_mrs(project):
    mrs = project.mergerequests.list()
    return mrs

#Create Commits object
class Commits:
    def __init__(self, id, short_id, title, created_at, author_email):
        self.id = id
        self.short_id = short_id
        self.title = title
        self.created_at = created_at
        self.author_email = author_email
  
#Create Issues object
class Issues:
    def __init__(self, id, project_id, title, state, created_at, updated_at):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.state = state
        self.created_at = created_at
        self.updated_at = updated_at  

#Create MRs/Pull-request object
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

#
def push_commit():
    projects = get_projects()
    for project in projects:
        commit = get_commits(project)
        #Check if project has no commit
        if len(commit) > 0: 
            for com in range(0, len(commit)):
                data = Commits(commit[com].id, commit[com].short_id, commit[com].title, commit[com].created_at, commit[com].author_email)
                with InfluxDBClient(url=influx_server, token=influx_token, org=org_name) as client: 
                    data_point = [{
                        "measurement": project.id,
                        "tags": {
                        "project_name": project.name,
                        "commit_id": data.id,
                        "commit_title": data.title,
                        "created_at": data.created_at,
                        "author_email": data.author_email,
                        },
                        "time": int(time()) * 1000000000,
                        "fields": {
                        "short_id": data.short_id
                        }
                    }]

                    try: 
                        client.write_api(write_options=ASYNCHRONOUS).write(bucket_name, org_name, data_point)
                        print ("write ", data_point," to bucket "+bucket_name)
                    except Exception as e:
                        print(e)


def push_issue():
    projects = get_projects()
    for project in projects:
        issue = get_issues(project)
        #Check if project has no issue
        if len(issue) > 0: 
            for isu in range(0, len(issue)):
                data = Issues(issue[isu].id, issue[isu].project_id, issue[isu].title, issue[isu].state, issue[isu].created_at, issue[isu].updated_at)
                with InfluxDBClient(url=influx_server, token=influx_token, org=org_name) as client: 
                    data_point = [{
                        "measurement": data.project_id,
                        "tags": {
                        "project_name": project.name,
                        "issue_id": data.id,
                        "issue_title": data.title,
                        "issue_state": data.state,
                        "created_at": data.created_at,
                        "updated_at": data.updated_at,
                        },
                        "time": int(time()) * 1000000000,
                        "fields": {
                        "issue_id": data.id
                        }
                    }]

                    try: 
                        client.write_api(write_options=ASYNCHRONOUS).write(bucket_name, org_name, data_point)
                        print ("write ", data_point," to bucket "+bucket_name)
                    except Exception as e:
                        print(e)


def push_mrs():
    projects = get_projects()
    for project in projects:
        mrs = get_mrs(project)
        #Check if project has no mrs
        if len(mrs) > 0: 
            for m in range(0, len(mrs)):
                data = Mrs(mrs[m].id, mrs[m].project_id, mrs[m].title, mrs[m].state, mrs[m].created_at, mrs[m].updated_at, mrs[m].target_branch, mrs[m].source_branch)
                with InfluxDBClient(url=influx_server, token=influx_token, org=org_name) as client: 
                    data_point = [{
                        "measurement": project.id,
                        "tags": {
                        "project_name": project.name,
                        "mrs_id": data.id,
                        "mrs_title": data.title,
                        "state": data.state,
                        "created_at": data.created_at,
                        "updated_at": data.updated_at,
                        "target_branch": data.target_branch,
                        "source_branch": data.source_branch,
                        },
                        "time": int(time()) * 1000000000,
                        "fields": {
                        "mrs_id": data.id
                        }
                    }]

                    try: 
                        client.write_api(write_options=ASYNCHRONOUS).write(bucket_name, org_name, data_point)
                        print ("write ", data_point," to bucket "+bucket_name)
                    except Exception as e:
                        print(e)

