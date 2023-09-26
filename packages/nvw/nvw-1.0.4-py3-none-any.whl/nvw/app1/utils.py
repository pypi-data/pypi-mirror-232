import subprocess
import json
import os

def get_topology_info(cwd, options) -> 'dict':
    cmd = os.environ['_NVIEW_TOPOLOGY_COMMAND']
    output_str = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=cwd).stdout
    output_json = json.loads(output_str)
    return output_json


