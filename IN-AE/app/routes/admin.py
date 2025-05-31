from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from app.models.restaurant import Restaurant
from app import db
from app.models.sensor_data import SensorData
from datetime import datetime, timedelta
import requests
import json
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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
        print(container_url)
        # Send POST request to create the content instance
        response = requests.post(
            container_url, 
            headers=header, 
            json=content_instance_payload, 
            verify=False
        )                
        if response.status_code == 201:
            print('Success')
            return True
        else:
            print(f"Failed to create Content Instance: {response.status_code} {response.text}")
            return False
            
    except Exception as e:
        print(f"Error creating Content Instance: {e}")
        return False


@admin_bp.route('/stats')
@login_required
def restaurant_stats():
    if not current_user.restaurant:
        abort(404)
    print(current_user.restaurant.current_hue)
    return render_template('admin/stats.html', 
                         restaurant=current_user.restaurant,
                         light_settings={
                             'hue': current_user.restaurant.current_hue,
                             'saturation': current_user.restaurant.current_saturation,
                             'lightness': current_user.restaurant.current_lightness,
                             'lux': current_user.restaurant.current_lux
                         })

@admin_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_restaurant():
   if not current_user.restaurant:
       abort(404)
   if request.method == 'POST':
       data = request.json
       restaurant = current_user.restaurant
       restaurant.name = data.get('name', restaurant.name)
       restaurant.description = data.get('description', restaurant.description)
       restaurant.address = data.get('address', restaurant.address)
       restaurant.latitude = data.get('latitude', restaurant.latitude)
       restaurant.longitude = data.get('longitude', restaurant.longitude)
       restaurant.image_path = data.get('image_path', restaurant.image_path)
       db.session.commit()
       return jsonify({'success': True})
   return render_template('admin/edit.html', restaurant=current_user.restaurant)

@admin_bp.route('/api/sensor-data', methods=['GET', 'POST'])
@login_required
def sensor_data():
   if request.method == 'POST':
       data = request.json
       if not data:
           return jsonify({'error': '데이터가 없습니다.'}), 400
           
       sensor_data = SensorData(
           restaurant_id=current_user.restaurant.id,
           temperature=data.get('temperature'),
           humidity=data.get('humidity'),
           noise_level=data.get('noise_level'),
           timestamp=datetime.strptime(data.get('timestamp'), '%Y%m%dT%H%M%S')
       )
       if not current_user.restaurant:
           abort(404)
       if request.method == 'POST':
           restaurant = current_user.restaurant
           restaurant.temperature = data.get('temperature')
           restaurant.noise_level = data.get('noise_level')
           restaurant.humidity = data.get('humidity')           
       db.session.add(sensor_data)
       db.session.commit()
       return jsonify({'success': True})

   # GET request - 센서 데이터 조회
   sensor_data = SensorData.query.filter_by(
       restaurant_id=current_user.restaurant.id
   ).order_by(SensorData.timestamp.desc()).limit(100).all()
   
   return jsonify([data.to_dict() for data in sensor_data])

@admin_bp.route('/api/update-lighting', methods=['POST'])
@login_required
def update_lighting():
    """
    조명 제어 값을 받아서 처리하는 엔드포인트
    HSL 색상값과 조도(Lux) 값을 받아서 처리합니다.
    """
    try:
        data = request.json
        
        # 슬라이더에서 전송된 값들을 가져옵니다
        hue = data.get('hue', 0)         # 색상 (0-360)
        saturation = data.get('saturation', 0)  # 채도 (0-100)
        lightness = data.get('lightness', 0)    # 밝기 (0-100)
        lux = data.get('lux', 0)         # 조도 (0-1000)        
        # 여기에서 실제 하드웨어 제어 함수를 호출합니다
        result = control_lighting(
            restaurant_id=current_user.restaurant.id,
            hue=hue,
            saturation=saturation,
            lightness=lightness,
            lux=lux
        )

        # 데이터베이스에 설정 값을 저장할 수 있습니다
        restaurant = current_user.restaurant
        restaurant.current_hue = hue
        restaurant.current_saturation = saturation
        restaurant.current_lightness = lightness
        restaurant.current_lux = lux
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '조명 설정이 업데이트되었습니다',
            'values': {
                'hue': hue,
                'saturation': saturation,
                'lightness': lightness,
                'lux': lux
            }
        })

    except Exception as e:
        pass
        # 오류 발생 시 로깅하고 에러 응답을 반환합니다

def control_lighting(restaurant_id, hue, saturation, lightness, lux):
    # Convert HSL to RGB and get the dictionary directly
    rgb_dict = hsl_to_rgb(hue, saturation, lightness)
    rgb_dict.update({"lux": lux})
    json_string = json.dumps(rgb_dict)
    create_content_instance(f"http://localhost:8080/~/{restaurant_id}/cse-mn/SmartBulb/command", json_string, "CAdmin")
    return True
        

def hsl_to_rgb(h, s, l):
    # Normalize values to 0-1 range
    h = h / 360
    s = s / 100
    l = l / 100

    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p

    # Handle special case when saturation is 0 (grayscale)
    if s == 0:
        r = g = b = l
    else:
        # Calculate intermediate values for RGB conversion
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    # Convert to 0-255 range and return as dictionary
    return {
        "r": int(r * 255), 
        "g": int(g * 255), 
        "b": int(b * 255)
    }