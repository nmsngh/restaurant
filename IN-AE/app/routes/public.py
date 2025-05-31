# app/routes/public.py
from flask import Blueprint, render_template, jsonify
from app.models.restaurant import Restaurant

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    restaurants = Restaurant.query.order_by(Restaurant.rating.desc()).all()
    return render_template('public/index.html', restaurants=restaurants)

@public_bp.route('/api/restaurants/<string:id>')
def get_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    return jsonify(restaurant.to_dict())

@public_bp.route('/restaurant/<string:id>')
def restaurant_detail(id):
    restaurant = Restaurant.query.get_or_404(id)
    return render_template('public/restaurant.html', restaurant=restaurant)