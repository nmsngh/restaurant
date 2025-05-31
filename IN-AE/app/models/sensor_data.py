from app import db
from datetime import datetime

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    noise_level = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'noise_level': self.noise_level,
            'timestamp': self.timestamp.strftime('%Y%m%dT%H%M%S')
        }