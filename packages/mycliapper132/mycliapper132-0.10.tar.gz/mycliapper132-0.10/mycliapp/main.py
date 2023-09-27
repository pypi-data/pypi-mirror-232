import click
from databricks import sql
import json
import hashlib
import hmac
import base64
import requests
from datetime import datetime
import pytz
from typing import List, Tuple

@click.command()
@click.option('--name', default='World', help='The person to greet.')
def hello(name):

   connection = sql.connect(
                           server_hostname = "adb-4524064152464769.9.azuredatabricks.net",
                           http_path = "/sql/1.0/warehouses/3d58d7311ef7752e",
                           access_token = "dapi35c10a821ebd811a52e94ebdcf47ee4f")

   cursor = connection.cursor()
   results = []
   cursor.execute("select distinct command_invocation_id, run_started_at from models order by run_started_at desc limit 2")
   result = cursor.fetchall()
   
   common_invocation_id = []
   for x in result:
     common_invocation_id.append(x['command_invocation_id'])
   
   list_of_id = ', '.join(['"{}"'.format(item) for item in common_invocation_id])

   print(f"select * from `model_executions` WHERE node_id NOT LIKE 'model.dbt_artifacts%' and command_invocation_id in ({list_of_id})") 
   cursor.execute(f"select * from `model_executions` WHERE node_id NOT LIKE 'model.dbt_artifacts%' and command_invocation_id in ({list_of_id})")
   results.append(list_to_dict(cursor.fetchall(),cursor.description))

   cursor.execute(f"select * from `seed_executions` WHERE node_id NOT LIKE 'model.dbt_artifacts%' and command_invocation_id in ({list_of_id})")
   results.append(list_to_dict(cursor.fetchall(),cursor.description))

   cursor.execute(f"select * from `test_executions` WHERE node_id NOT LIKE 'model.dbt_artifacts%' and command_invocation_id in ({list_of_id})")
   results.append(list_to_dict(cursor.fetchall(),cursor.description))

   cursor.execute(f"select * from `snapshot_executions` WHERE node_id NOT LIKE 'model.dbt_artifacts%' and command_invocation_id in ({list_of_id})")
   results.append(list_to_dict(cursor.fetchall(),cursor.description))

   flattened_list = [item for sublist in results for item in sublist]

   stud_json = json.dumps(flattened_list, indent=2)
   print(stud_json)
   cursor.close()
   connection.close()

#    send_custom_data("dbtlogs",stud_json)

def list_to_dict(list, description: List[Tuple]):
    result = []
    for row in list:
      result_dict = {}
      for i, column in enumerate(description):
         result_dict[column[0]] = str(row[i])
      result.append(result_dict)
    return result

def send_custom_data(log_name, data):
    json_request_data = data
    server_time_string = get_server_time()
    signature = get_request_signature(server_time_string, json_request_data)
    print(signature)
    url = f"https://ad5bbf1f-9526-44c8-84a6-2bcfce06eb68.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
    headers = {
        "Authorization": signature,
        "Content-Type": "application/json",
        "Log-Type": log_name,
        "x-ms-date": get_x_ms_date(),
        "time-generated-field": "LogGeneratedTime",
    }
    try:
        response = requests.post(url, headers=headers, data=json_request_data)
        status_code = response.status_code
        if status_code != 200:
            raise RuntimeError("Unable to send custom log data to Azure Monitor")
    except Exception as e:
        raise e
    

def get_request_signature(server_time_string, request_data):
    http_method = "POST"
    content_type = "application/json"
    xms_date = f"x-ms-date:{server_time_string}"
    resource = "/api/logs"
    string_to_hash = "\n".join([http_method, str(len(request_data.encode("utf-8"))), content_type, xms_date, resource])
    hashed_string = get_hmac256(string_to_hash, "bsQgCl3L//hNfHJHYi5Eurqx1OcHfkGYbbj3X6UBgD5AFXSkNT6EsQ/MZsy/VAqM6sW7fzkf9rdO5nY13kT3nA==")
    return f"SharedKey ad5bbf1f-9526-44c8-84a6-2bcfce06eb68:{hashed_string}"


def get_server_time():
    now = datetime.utcnow()
    return now.strftime("%a, %d %b %Y %H:%M:%S GMT")

def get_hmac256(input_string, key):
    sha256_hmac = hmac.new(base64.b64decode(key.encode("utf-8")), input_string.encode("utf-8"), hashlib.sha256)
    return base64.b64encode(sha256_hmac.digest()).decode("utf-8")


def get_x_ms_date():
    utc_now = datetime.now(pytz.timezone('UTC'))
    formatted_date = utc_now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return formatted_date

if __name__ == '__main__':
   hello()