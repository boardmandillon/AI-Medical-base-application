from flask import redirect, url_for, request, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_login import current_user


# class BaseAdminIndexView(AdminIndexView):
#     @expose('/admin')
#     def index(self):
#         if not current_user.is_authenticated():
#             return redirect(url_for('login', next_page=request.url))
#
#         return super(BaseAdminIndexView, self).index()


class AdminModelView(ModelView):

    def is_accessible(self):
        # TODO: #23 Separate admin users and regular users
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next_page=request.url))
