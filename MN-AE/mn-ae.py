from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json
from datetime import datetime
import threading
import time
from functools import wraps
import os
import warnings

warnings.filterwarnings('ignore')
CONFIG = {
    'IN_CSE_HOST': os.getenv('IN_CSE_HOST'),
    'IN_CSE_PORT': os.getenv('IN_CSE_PORT'),
    'LOCAL_HOST': os.getenv('LOCAL_HOST'),
    'LOCAL_PORT': os.getenv('LOCAL_PORT'),
    'AUTH_TOKEN': os.getenv('AUTH_TOKEN'),
    'MN_ORIGINATOR': os.getenv('MN_ORIGINATOR'),
    'MN_CSE_HOST': os.getenv('MN_CSE_HOST'),
    'MN_CSE_PORT': os.getenv('MN_CSE_PORT')
}
CONFIG['IN_CSE_HOST'] = '172.28.6.239' #2025
CONFIG['IN_CSE_PORT'] = '8080'
CONFIG['MN_ORIGINATOR'] = 'CAdmin'
CONFIG['LOCAL_HOST'] = '172.19.0.39' #2025
CONFIG['LOCAL_PORT'] = '5000'
CONFIG['AUTH_TOKEN'] = 'osori'
# URLs

IN_CSE_URL = f"http://{CONFIG['IN_CSE_HOST']}:{CONFIG['IN_CSE_PORT']}/cse-in"
NOTIFICATION_URL = f"http://{CONFIG['LOCAL_HOST']}:{CONFIG['LOCAL_PORT']}/notifi"

app = Flask(__name__)
CORS(app)
app = Flask(__name__)
CORS(app)
ts_id = [] 

# Token Authentication Decorator
def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization token"}), 401
        
        token = auth_header.split('Bearer ')[1]
        if token != CONFIG['AUTH_TOKEN']:
            return jsonify({"error": "Invalid token"}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def create_headers(originator: str, resource_type: str = None, request_id: str = None, time: str = None, rsc: str = None) -> dict:
    headers = {
        "Accept": "application/json",
        "X-M2M-Origin": originator,
        "X-M2M-RVI": "3",
        "Authorization": f"Bearer {CONFIG['AUTH_TOKEN']}"
    }

    if rsc:
        headers["X-M2M-RSC"] = rsc

    if resource_type:
        headers["Content-Type"] = 'application/json;ty=' + resource_type

    if request_id:
        headers["X-M2M-RI"] = request_id

    if time:
        headers["'X-M2M-OT'"] = time

    return headers

def register_mn_ae(mn_ae_ori): #mn-ae에대한 ae를 in-cse에 생성 요청하는 코드 // NO DEBUGGING
    # mn_ae_ori = "myRestaurant1" #환경변수로 따로 설정필요->레스토랑 이름으로 입력시키면 아주 간편
    header = create_headers(f"C{mn_ae_ori}", '2', 'create_ae')

    payload = {
        "m2m:ae": {
            "rn": mn_ae_ori,
            "api": f"N{mn_ae_ori}.myapp",
            "lbl": ["test"],
            "rr": True,
            "srv": ["2a", "3", "4"]
        }
    }
    
    response = requests.post(IN_CSE_URL, headers=header, json=payload, verify=False)
    if response.status_code == 201:
        print("message: AE 등록 성공\n data:", response.json())
        return True
    
    return False

def create_container(ae_rn, ae_url, sensor):
    header = create_headers( "ae_rn", '3', 'create_cnt')
    container_payload = {
        "m2m:cnt": {
            "rn": sensor
        }
    }

    response = requests.post(ae_url, headers=header, json=container_payload, verify=False)
    if response.status_code == 201:
        print(f"Container '{sensor}' created successfully under AE {ae_url}")
    else:
        print(f"Failed to create container '{sensor}': {response.status_code} {response.text}")



def create_subscription():
    time.sleep(2)
    subscription_url = IN_CSE_URL
    header = create_headers(CONFIG['MN_ORIGINATOR'], '23', 'create_sub')
    subscription_payload = {
        "m2m:sub": {
            "rn": "aeSubscription",
            "nu": [NOTIFICATION_URL],
            "nct": 1,
            "enc": {
                "net": [3]
            }
        }
    }
    
    responses = requests.get(
        subscription_url, 
        headers={"X-M2M-Origin": CONFIG['MN_ORIGINATOR'], 
                "Accept": "application/json",
                "X-M2M-RVI": "3", #2025
                "Authorization": f"Bearer {CONFIG['AUTH_TOKEN']}"}, 
        verify=False
    )
    
    if responses.status_code == 409:
        print("Subscription already exists. Skipping creation.")
        return

    response = requests.post(subscription_url, headers=header, json=subscription_payload, verify=False)
    if response.status_code == 201:
        print("Subscription created successfully!")
    else:
        print(f"Failed to create subscription: {response.status_code} {response.text}")

@app.route('/notifi', methods=['POST'])
#@require_token
def handle_notification():
    global ts_id
    notification = request.get_json()
    print(f"Notification received: {json.dumps(notification, indent=4)}")

    if notification.get("m2m:sgn", {}).get("vrq", False):

        content_type = request.headers.get('Content-Type', '').lower()
        notification_data = request.json
        
        print("Received Notification:", notification_data)
        print("Headers:", dict(request.headers))

        register_mn_ae('Sensors')
        time.sleep(1)
        register_mn_ae('SmartBulb')
        time.sleep(1)
        handle_registration('Sensors','CSensors')
        time.sleep(1)
        handle_registration('SmartBulb','CSmartBulb') 

        header = create_headers(
            originator='mn-ae',
            rsc='2000',
            request_id=request.headers.get('X-M2M-RI', '')
        )

        return Response(status=200, headers=header)
    
    return jsonify({"status": "success"}), 200
    
def handle_registration(new_ae_rn, new_ae_ri):
    
    if not new_ae_rn:
        print("AE Resource Name (rn) is missing in the notification.")

    if new_ae_rn=="SmartBulb": #생성된 ae의 이름이 smartBulb일 경우
        cnt_name = "command"
        ae_url = f"{IN_CSE_URL}/{new_ae_rn}"
        create_container(new_ae_rn, ae_url, cnt_name)
    elif new_ae_rn == "Sensors": # 그외의 센서가 ae로 등록될 경우
        sensor_names = ["temperature", "humid", "noise"]
        for sensor in sensor_names:
            ae_url = f"{IN_CSE_URL}/{new_ae_rn}"
            create_container(new_ae_rn, ae_url, sensor)
            

init_task_done = threading.Event()

def start_init_tasks():
    global ts_id
    if not init_task_done.is_set():
        create_subscription()
        time.sleep(2) 
       
        init_task_done.set()

if __name__ == '__main__':
    threading.Thread(target=start_init_tasks).start()
    app.run(host='0.0.0.0', debug=True, port=int(CONFIG['LOCAL_PORT']))
