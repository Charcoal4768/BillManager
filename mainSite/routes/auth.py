from flask import Blueprint, request, render_template, redirect, url_for, flash
from mainSite import socket
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import generate_csrf, validate_csrf
from mainSite.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        # Handle login logic
        phone = request.form['phone']
        password = request.form['password']
        user = User.get_by_phone(phone)
        # Check fields first
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('views.home'))
        flash('Wrong phone number or password.', 'danger')
    csrf_token = generate_csrf()
    return render_template('login.html', csrf_token=csrf_token, user=current_user)

@login_required
@auth_bp.route('/logout')
def logout():
    # Handle logout logic
    logout_user()
    return redirect(url_for('views.home'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        try:
            validate_csrf(csrf_token)
        except:
            flash('Invalid CSRF token.', 'danger')
            return redirect(url_for('auth.login'))
        # Handle signup logic
        name = request.form['username']
        gstno = request.form['gstno']
        password = request.form['password']
        password2 = request.form['password2']
        phone = request.form['phone']
        address = request.form['address-line1']
        address2 = request.form['address-line2']
        #min length check for all fields
        if len(name) < 2 or len(password) < 6 or len(phone) < 9:
            flash('Please fill out all fields correctly.', 'warning')
            return redirect(url_for('auth.signup'))
        if not password:
            flash('Passwords are mandatory.', 'danger')
            return redirect(url_for('auth.signup'))
        if password != password2:
            flash('Passwords dont match', 'warning')
            return redirect(url_for('auth.signup'))
        user = User.get_by_phone(phone)
        if user:
            flash('Phone Number already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User.create_user(name=name, phone=phone, addr=address+'\n'+address2, gstno=gstno, password=hashed_password)
        login_user(new_user)
        flash(f'Signed up as {name}! You can now add more details.', 'success')
        return redirect(url_for('views.home'))
    csrf_token = generate_csrf()
    return render_template('signup.html', csrf_token=csrf_token, user=current_user)
