from typing import List, Tuple

import json
import requests
import time

from . import api_key

class JobClient:
    
    def __init__(self, job_id: str, options: List[Tuple[str,str]] = []):
        self.job_id = job_id
        self.options = options
        
    def __call__(self, **kwargs):
        for option in self.options:
            assert option[0] in kwargs, f"Missing option {option[0]}"
            if option[1] == "file":
                # Three cases: str (path), file-like object, or bytes
                if isinstance(kwargs[option[0]], str):
                    with open(kwargs[option[0]], "rb") as f:
                        kwargs[option[0]] = f.read()
                elif hasattr(kwargs[option[0]], "read"):
                    kwargs[option[0]] = kwargs[option[0]].read()
                elif isinstance(kwargs[option[0]], bytes):
                    pass
                else:
                    raise ValueError(f"Invalid type for {option[0]}, must be str (path), file-like object, or bytes")
            elif option[1] == "json":
                kwargs[option[0]] = json.dumps(kwargs[option[0]])
            else:
                raise ValueError(f"""Invalid type for {option[0]}, currently specified as {option[1]} must be "file" or "json" """)
            
        files = {
            option[0]: kwargs[option[0]]
            for option in self.options
        }
        
        response = requests.post("https://api.hermsea.com/beta/v1/jobs", headers={
            "X-API-Key": api_key,
            "X-Herm-ID": self.job_id,
        }, files=files)
        
        body = json.loads(response.json()['body'])
        jobinstanceid = body['jobinstanceid']
        print("Job instance ID:", jobinstanceid)
        result = None
        interval = 0.01
        while result is None:
            response2 = requests.get("https://api.hermsea.com/beta/v1/jobs/status", 
                    params={"jobinstanceid": jobinstanceid},
                    headers={
                        "X-API-Key": api_key,
                        "Content-Type": "application/json",
                    }
                )
            result = response2.json()[0]
            time.sleep(interval)
            interval = min(interval * 2, 1)
        
        return result