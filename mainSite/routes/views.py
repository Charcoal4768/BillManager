from flask import Flask, Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import current_user
from mainSite import socket

views_bp = Blueprint('views', __name__)

@views_bp.route('/', methods=['GET'])
def home():
    return render_template('home.html', user=current_user)

@views_bp.route('/about', methods=['GET'])
def about():
    return render_template('about.html', user=current_user)

@views_bp.route('/home', methods=['GET'])
def redirect_to_home():
    return redirect(url_for('views.home'))

@views_bp.route('/billing', methods=['GET'])
def billing():
    pass

@views_bp.route('/settings', methods=['GET','POST'])
def user_settings():
    return render_template('profile.html', current_user=current_user)