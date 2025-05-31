from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.models.restaurant import Restaurant

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/restaurants')
@login_required
def list():
    restaurants = Restaurant.query.order_by(Restaurant.rating.desc()).all()
    return render_template('restaurants.html', restaurants=restaurants)

@restaurant_bp.route('/api/restaurants/<int:restaurant_id>')
@login_required
def get_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return jsonify(restaurant.to_dict())