# app/routes/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.restaurant_stats'))
        
    if request.method == 'POST':
        restaurant_id = request.form.get('restaurant_id')
        password = request.form.get('password')
        
        if not restaurant_id or not password:
            flash('레스토랑 ID와 비밀번호를 모두 입력해주세요.')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(id=restaurant_id).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.restaurant_stats'))
        
        flash('잘못된 레스토랑 ID 또는 비밀번호입니다.')
        return redirect(url_for('auth.login'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))