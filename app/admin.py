from flask import redirect, url_for, request, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_admin.helpers import is_form_submitted
from flask_login import current_user
from wtforms import fields, validators


class BaseAdminIndexView(AdminIndexView):
    """Admin index view, which adds authentication to the admin site."""

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class AdminModelView(ModelView):
    """Basic model view with authentication for database models to use."""

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

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

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.set_password(form.password.data)
        return model

    def validate_form(self, form):
        if is_form_submitted() and "email" in form.data:
            _id = request.values.get('id')
            users = self.model.query.filter_by(email=form.email.data).all()

            # Ignore user with the same email if its the user being edited
            if _id and users:
                users = list(filter(lambda u: (u.id != int(_id)), users))

            if users:
                flash("Please use a different email address.",
                      category="error")
                return False

        return super(AdminModelView, self).validate_form(form)
