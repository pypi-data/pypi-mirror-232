import herm
import os

def test_find_api_key():
    herm.api_key = "HELLO1"
    assert herm.api_key == "HELLO1"    
    
def test_jobs_post():
    import requests
    import json
    import time
    
    response = requests.post("https://api.hermsea.com/beta/v1/jobs", headers={
        "X-API-Key": herm.api_key,
        "X-Herm-ID": "befe8b5d-54c8-4a36-85d1-a921af98994f",
        "Content-Type": "multipart/form-data",
    })
    print(response)
    assert response.status_code == 200
    print(response.json())
    
    body = json.loads(response.json()['body'])
    jobinstanceid = body['jobinstanceid']
    time.sleep(6)
    
    response = requests.get("https://api.hermsea.com/beta/v1/jobs/status", 
                params={"jobinstanceid": jobinstanceid},
                headers={
                    "X-API-Key": herm.api_key,
                    "Content-Type": "application/json",
                }
            )
    print(response)
    assert response.status_code == 200
    print(response.json())
    assert response.json()[0] == "TEST done"
    
def test_basic_jobclient():
    from herm import JobClient
    
    TestFunc = JobClient("befe8b5d-54c8-4a36-85d1-a921af98994f")
    
    result = TestFunc()
    
    assert result == "TEST done"