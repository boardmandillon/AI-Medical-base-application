from flask import redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user

from wtforms import fields, validators


class BaseAdminIndexView(AdminIndexView):
    """Admin index view, which adds authentication to the admin site."""

    def is_accessible(self):
        return not current_user.is_anonymous and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class AdminModelView(ModelView):
    """Basic model view with authentication for database models to use."""

    def is_accessible(self):
        return not current_user.is_anonymous and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class UserModelView(AdminModelView):
    """Model view for the User model."""
    column_exclude_list = ['password_hash', 'token', 'token_expiration']
    column_searchable_list = ['name', 'email']
    column_filters = ['user_role']
    form_excluded_columns = column_exclude_list

    def get_create_form(self):
        create_form = super().get_create_form()

        create_form.email = fields.StringField(
            'Email', validators=[
                validators.DataRequired(), validators.Email()])
        create_form.password = fields.PasswordField(
            'Password', validators=[validators.DataRequired()])
        create_form.password_confirm = fields.PasswordField(
            'Confirm Password', validators=[
                validators.DataRequired(), validators.EqualTo('password')])

        return create_form
