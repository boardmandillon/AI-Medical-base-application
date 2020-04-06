from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app.auth import bp
from app.models.user import User
from app.auth.forms import LoginForm


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page for logging in as a user."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    else:
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            if not user or not user.check_password(form.password.data) or \
                    not user.is_admin():
                flash('Invalid username or password')

                return redirect(url_for('auth.login'))
            else:
                login_user(user, remember=form.remember_me.data)

                next_page = request.args.get('next')
                # If next page has been set; make sure its not malicious
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('admin.index')

                return redirect(next_page)

        return render_template(
            'auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    """Log user out."""
    logout_user()
    return redirect(url_for('auth.login'))
