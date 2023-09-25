import boto3
import json
from datetime import datetime


class ValueMember:
    def __init__(self, name, values, store_name=None):
        self.name = name
        self.values = set(values)
        self.store_name = store_name or ('_' + name)
         
    def __get__(self, obj):
        return getattr(obj, self.store_name)
     
    def __set__(self, obj, value):
        if value not in self.values:
            raise ValueError('Invalid value for', self.name,
                            'Expected one of', self.values,
                            'got', value)
        setattr(obj, self.store_name, value)

class HydraJobStatus:
    status = ValueMember('status', ["START", "SUCCESS", "FAILURE"])

class HydraEnvironment:
    environment = ValueMember('environment', ["DEV","QA","STAG","PROD"])

ebclient = boto3.client('events', region_name="us-east-1")

# Empty Payload
payload = {"version": "1.0"}


def add_project_metadata(project, app, dataset, jobid, dayid=None):
    
    payload["meta"] = {}
    payload["meta"]["project"] = project
    payload["meta"]["app"] = app
    payload["meta"]["dataset"] = dataset
    payload["meta"]["jobid"] = jobid
    
    if dayid is None:
        pass 
    else:
        payload["meta"]["partition"] = {}
        payload["meta"]["partition"]["dayId"] = dayid

    print(payload) 


def post_job_status(environment, status, source = None, input=None, output = None):
    
    try:
        varsource = payload["meta"]["project"] if source is None else source
    except KeyError:
        raise Exception("Project Metadata values not updated, use update_project_metadata() to update metadata values")

    starttime = datetime.today().strftime('%Y-%m-%d %H:%M:%S.%f%z')
    starttime = starttime[0:23] + '+0000'

    payload["timestamp"] = starttime

    hydra_env = HydraEnvironment()
    hydra_env.environment = environment.upper()
    event_busname = "hydra-job-status" if environment.upper() == "PROD" else "hydra-job-status-qa"

    print("Event Bus:", event_busname)

    hydra_job_status = HydraJobStatus()
    hydra_job_status.status = status
    payload["status"] = status

    payload["input"] = [] if input is None else input
    payload["output"] = [] if output is None else output

    print(payload)

    try:
        resp = ebclient.put_events(Entries=[{
                                            "Source": varsource,
                                            "DetailType": "job-status",
                                            "Detail": json.dumps(payload),
                                            "EventBusName": event_busname
                                        }]
        )
        FailedEntryCount = resp['FailedEntryCount']
        HTTPStatusCode = resp['ResponseMetadata']['HTTPStatusCode']
   
        if FailedEntryCount == 0 and HTTPStatusCode == 200:
            return 'Success'
        else:
            raise Exception('Hydra Job Status update Failure', resp)   
    except Exception as Err:
        raise Exception(Err)
    
                          
def add_dq_metric(type, column, value, status, threshold=None, actual=None):
    pass
    

def post_dq_metrics(status):
    pass


