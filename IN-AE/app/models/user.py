# app/models/user.py
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.String(50), primary_key=True)  # restaurant_id를 id로 사용
    password_hash = db.Column(db.String(128), nullable=False)
    restaurant_id = db.Column(db.String(50), db.ForeignKey('restaurant.id'), unique=True)
    
    # 관계 설정
    restaurant = db.relationship('Restaurant', backref=db.backref('manager', uselist=False))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_user(restaurant_id, password):
        user = User(id=restaurant_id, restaurant_id=restaurant_id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user