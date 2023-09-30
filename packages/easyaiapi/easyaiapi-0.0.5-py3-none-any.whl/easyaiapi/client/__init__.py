from .client import WssClient
import json
from typing import Optional
import base64
import requests

def post_file_to_api(url: str, name:str, content: bytes, additional_data:Optional[dict]=None, additional_headers:Optional[dict]=None):
    
    headers = {'Content-type': 'application/json'}
    if isinstance(additional_headers, dict):
        headers.update(**additional_headers)

    payload = json.dumps({
        name: base64.b64encode(content).decode("utf8"),
        **(additional_data or {})
    })
    response = requests.post(
        url, 
        data=payload,
        headers=headers
    )
    return response

def post_file_to_api_from_path(url: str, name:str, path: str, additional_data:Optional[dict]=None, additional_headers:Optional[dict]=None):
    return post_file_to_api(url, name, open(path, 'rb').read(), additional_data, additional_headers)
