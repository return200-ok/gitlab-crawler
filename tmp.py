def gen_datapoint(kpi, i):
    match kpi:
        case "mrs":
            data = Mrs(mrs[i].id, mrs[i].project_id, mrs[i].title, mrs[i].state, mrs[i].created_at, mrs[i].updated_at, mrs[i].target_branch, mrs[i].source_branch)
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
            return data_point
        case "issue":
            data = Issues(issue[i].id, issue[i].project_id, issue[i].title, issue[i].state, issue[i].created_at, issue[i].updated_at)
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
            return data_point
        case "commit":
            data = Commits(commit[i].id, commit[i].short_id, commit[i].title, commit[i].created_at, commit[i].author_email)
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
                "commit_id": data.short_id
                }
            }]
            return data_point


def push_data(list_kpi):
    if len(list_kpi) > 0: 
        for i in range(0, len(list_kpi)):
            with InfluxDBClient(url=influx_server, token=influx_token, org=org_name) as client: 
                gen_datapoint(list_kpi, i)
                try: 
                    client.write_api(write_options=ASYNCHRONOUS).write(bucket_name, org_name, data_point)
                    logging.info("write "+str(data_point)+" to bucket "+bucket_name)
                except Exception as e:
                    logging.exception(e)


projects = get_projects()
for project in projects:
    kpis = ["mrs","issue","commit"]
    for kpi in kpis:
        match kpi:
            case "mrs":
                list_kpi = get_mrs(project)
                push_data(list_kpi)