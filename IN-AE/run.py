from app import create_app, db
from app.models.user import User
from app.models.restaurant import Restaurant
import requests
import time
from datetime import datetime
from flask_login import login_required, current_user
import json
from app.models.sensor_data import SensorData
import threading
import os
app = create_app()

IN_CSE_URL = "http://172.28.6.239:8080/cse-in" #2025

def init_db():
   with app.app_context():
       db.create_all()
       
       # 샘플 레스토랑 데이터 생성
       restaurants_data = [
            {
                'id': 'C97f3b907ae2f8f9709f527a143156247f2d43f4c97c26ddde57cd06ebdbc21c9',
                'name': 'Delicious Korean Restaurant',
                'description': 'A fine dining establishment offering modern interpretations of traditional Korean cuisine. Enjoy elegant Korean table settings with seasonal special menus.',
                'image_path': 'images/1.jpg',
                'rating': 4.5,
                'address': '123-45 Yeoksam-dong, Gangnam-gu, Seoul',
                'latitude': 37.5012,
                'longitude': 127.0396,
                'temperature': 23.5,
                'humidity': 45.0,
                'noise_level': 65.0,
                'short_reviews': [
                    "Great for romantic dining on special occasions"
                ]
            },
            {
                'id': 'C8759909342aee5bc8b44ddd0f356ba796f076d2e386b5e4cc818af9f821e1e56',
                'name': 'Italian Kitchen',
                'description': 'An atmospheric restaurant serving authentic Italian cuisine. Wine pairing is available with selections personally curated by the chef.',
                'image_path': 'images/2.jpg',
                'rating': 4.8,
                'address': '456-78 Seocho-dong, Seocho-gu, Seoul',
                'latitude': 37.4923,
                'longitude': 127.0292,
                'temperature': 22.0,
                'humidity': 40.0,
                'noise_level': 58.0,
                'short_reviews': [
                    "Perfect for a romantic dinner on your special day"
                ]
            }          
       ]
       
       # 레스토랑과 관리자 계정 생성
       for rest_data in restaurants_data:
           restaurant_id = rest_data['id']
                      
           if not Restaurant.query.get(restaurant_id):
               restaurant = Restaurant(**rest_data)
               db.session.add(restaurant)                              
               if not User.query.get(restaurant_id):
                   user = User.create_user(restaurant_id, "password")  
       db.session.commit()

def send_get_request(url: str = "", originator: str = 'cse-in'):
    headers = {
        "Accept": "application/json",
        "X-M2M-RI": "12345",
        "X-M2M-Origin": originator,
        "X-M2M-RVI": "3"
    }
    
    try:        
        response = requests.get(url, headers=headers, verify=False)                
        print(response.json())
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

def create_headers(originator: str, resource_type: str = None, request_id: str = None, time: str = None, rsc: str = None) -> dict:
    headers = {
        "Accept": "application/json",
        "X-M2M-Origin": originator,
        "X-M2M-RVI": "3"        
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

def create_content_instance(container_url, data, originator):
    # Create headers with resource type 4 for content instance
    # The resource type 4 is specifically for content instances in oneM2M
    header = create_headers(originator, '4', '12345')
    content_instance_payload = {
        "m2m:cin": {
            "con": data  # The actual data/content to be stored
        }
    }
    try:
        # Send POST request to create the content instance
        response = requests.post(
            container_url, 
            headers=header, 
            json=content_instance_payload, 
            verify=False
        )
        print(response.json())
        # Check if creation was successful (201 Created)
        if response.status_code == 201:
            return True
        else:
            print(f"Failed to create Content Instance: {response.status_code} {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error creating Content Instance: {e}")
        return False


def generate_environment_description(temp, humidity, noise):
    description = []
    
    # Temperature description
    if temp >= 30:
        description.append("sauna-like hot")
    elif temp >= 25:
        description.append("warm")
    elif temp >= 20:
        description.append("comfortable")
    elif temp >= 15:
        description.append("cool")
    else:
        description.append("refrigerator-like cold")
        
    # Humidity description
    if humidity >= 70:
        description.append("rainforest-level humid")
    elif humidity >= 60:
        description.append("slightly humid")
    elif humidity >= 40:
        description.append("perfectly balanced humidity")
    else:
        description.append("dry")
        
    # Noise level description
    if noise >= 100:
        description.append("fighter jet takeoff-like noisy")
    elif noise >= 80:
        description.append("subway station-like busy")
    elif noise >= 60:
        description.append("cafe-level lively")
    elif noise >= 40:
        description.append("conversation-friendly quiet")
    else:
        description.append("library-like peaceful")

    # Generate final description
    final_description = " and ".join(description) + " atmosphere"
    
    return final_description


def sync_data():    
    time.sleep(3)    
    with app.app_context():    
        while True:
            sensor_name = ['temperature','humid','noise']
            sensor_map = {
            "temperature": "temp",
            "humid": "humidity",
            "noise": "noise"
            }   
            total = {}
            for sensor in sensor_name:
                url = f"{IN_CSE_URL}/Sensors/{sensor}/la"
                try:
                    res = send_get_request(url, "CAdmin").json()["m2m:cin"]
                    content = res['con']  
                    parsed = json.loads(content)
                    mapped_key = sensor_map[sensor]
                    total[sensor] = float(parsed.get(mapped_key))

            
                except Exception as e:
                    print(f"{sensor} 데이터 조회 실패: {e}")
                    total[sensor] = None

            sensor_data = SensorData(
                restaurant_id='C97f3b907ae2f8f9709f527a143156247f2d43f4c97c26ddde57cd06ebdbc21c9',
                temperature=total["temperature"],
                humidity=total["humid"],
                noise_level=total["noise"],
                timestamp=datetime.now()
            )    
            print(datetime.now())
            db.session.add(sensor_data)

            user = User.query.get('C97f3b907ae2f8f9709f527a143156247f2d43f4c97c26ddde57cd06ebdbc21c9')
            if user:
                user.restaurant.temperature = total["temperature"]
                user.restaurant.humidity = total["humid"]
                user.restaurant.noise_level = total["noise"]
                review = generate_environment_description(total["temperature"], total["humid"], total["noise"])
                print(review)
                user.restaurant.short_reviews = [review]

            db.session.commit()
            time.sleep(7)
    

if __name__ == '__main__':    
    init_db()  # 서버 시작 시 데이터베이스 초기화
    threading.Thread(target=sync_data).start()
    app.run(debug=False, host= '0.0.0.0', port = '18080')
