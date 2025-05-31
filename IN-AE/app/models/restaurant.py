from app import db
import datetime

class Restaurant(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0.0)
    address = db.Column(db.String(200))
    latitude = db.Column(db.Float)  # 위도
    longitude = db.Column(db.Float)  # 경도
    temperature = db.Column(db.Float)  # 현재 온도
    humidity = db.Column(db.Float)  # 현재 습도
    noise_level = db.Column(db.Float)  # 현재 소음 레벨 (dB)
    short_reviews = db.Column(db.JSON)  # 한줄평 목록
    current_hue = db.Column(db.Integer, default=180)
    current_saturation = db.Column(db.Integer, default=50)
    current_lightness = db.Column(db.Integer, default=50)
    current_lux = db.Column(db.Integer, default=500)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_path': self.image_path,
            'rating': self.rating,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'noise_level': self.noise_level,
            'short_reviews': self.short_reviews
        }