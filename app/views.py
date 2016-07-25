#!/usr/bin/env python
# coding: utf-8

import os

from flask import flash, g, Markup, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import application, hashing, login_manager, models


@application.before_request
def before_request():
    g.user = current_user


@application.route('/', methods=['GET'])
def home():
    return redirect(url_for('sign_in'))


@application.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = unicode(request.form['username'])
        password = unicode(request.form['password'])

        if username is None or not username:
            flash(Markup('<strong>Psst!</strong> You forgot username.'), 'warning')
        elif password is None or not password:
            flash(Markup('<strong>Psst!</strong> You forgot password.'), 'warning')
        else:
            user = models.Users.query.filter_by(username=username).first()

            if user is None:
                flash(Markup("<strong>Oops!</strong> The username and password don't match."), 'danger')
            else:
                if not hashing.check_value(user.password, password, user.salt):
                    flash(Markup("<strong>Oops!</strong> The username and password don't match."), 'danger')
                elif not login_user(user):
                    flash(Markup('<strong>Ugh!</strong> ' + str(user.name) + ', your account is banned.'), 'danger')
                else:
                    flash(Markup('<strong>Welcome ' + str(g.user.name) + '!</strong>'), 'success')

                    return redirect(url_for('dashboard'))

    return render_template('sign_in.html')


@application.route('/sign_out', methods=['GET'])
@login_required
def sign_out():
    logged_name = str(g.user.name)

    logout_user()

    flash(Markup('<strong>Bye, bye ' + logged_name + '!</strong> Come back soon!'), 'success')

    return redirect(url_for('sign_in'))


@application.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@application.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template('settings.html')


@application.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    app_directory = os.path.abspath(os.path.dirname(__file__))
    avatar = url_for('static', filename='img/' + g.user.username + '.png')

    if not os.path.exists(app_directory + avatar):
        avatar = url_for('static', filename='img/avatar.png')

    return render_template('profile.html', user=g.user, avatar=avatar)


@application.route('/about', methods=['GET'])
@login_required
def about():
    return render_template('about.html')


@login_manager.user_loader
def user_loader(id):
    return models.Users.query.get(id)
