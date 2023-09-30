from flask import redirect, url_for, abort, request
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.menu import BaseMenu, MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import FilterLike
from flask_security import current_user
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, SubmitField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired


from . import models, db
from .control import distribute_task
from .util.helpers import get_object_from_arg

class AdminModelView(ModelView):

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('admin')
        )

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))

class RightAlignedMenuLink(MenuLink):
    """
        Link item
    """
    def __init__(self, name, url=None, endpoint=None, category=None, class_name=None,
                 icon_type=None, icon_value=None, target=None):
        super(MenuLink, self).__init__(name, class_name, icon_type, icon_value, target)

        self.category = category

        self.url = url
        self.endpoint = endpoint

        self.class_name += ' navbar-right'

class AdminUserView(AdminModelView):
    can_create = False
    column_list = ('name', 'username', 'assignment_weight', 'email')
    form_columns = ('name', 'username', 'assignment_weight', 'groups', 'email', 'active')

    @property
    def can_delete(self):
        return current_user.has_permission('user_delete')

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_permission('user_read_all'))
        )


status_like = FilterLike(models.Task._status, name="Status")

class AdminTaskView(AdminModelView):
    column_filters = ('users.name', 'tracking_id', 'create_time', 'project', 'template.label', status_like)
    column_labels = {'users.name': 'User name', 'template.label':'Template label', 'create_time':'Create time'}
    column_searchable_list = ('users.name', 'template.label')
    column_list = ('id', 'tracking_id', 'project', 'template', 'users', '_status')
    form_columns = ('id', 'tracking_id', 'project', 'template', 'tags', 'raw_content', 'content', 'raw_callback_url', 'callback_url', 'callback_content', 'users')

    form_widget_args = {
        'tracking_id': {
            'disabled': True
        },
        'content': {
            'disabled': True
        },
        'callback_content': {
            'disabled': True
        },
        'callback_url': {
            'disabled': True
        }
    }

    @property
    def can_create(self):
        return False

    @property
    def can_edit(self):
        return current_user.has_permission('task_update_all')

    @property
    def can_delete(self):
        return current_user.has_role('admin')

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_permission('task_read_all'))
        )

    def edit_form(self, obj=None):
        form = super(AdminTaskView, self).edit_form(obj)
        form.users.query = db.session.query(models.User).filter(models.User.active).all()
        form.users.choices = form.users.query
        return form

class AdminGroupView(AdminModelView):
    column_list = ('groupname', 'name', 'create_time')
    form_columns = ('id','groupname', 'name', 'users', 'create_time')

    @property
    def can_create(self):
        return current_user.has_permission('group_add')

    @property
    def can_edit(self):
        return current_user.has_permission('group_update')

    @property
    def can_delete(self):
        return current_user.has_permission('group_delete')

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_permission('group_read_all'))
        )

class AdminMetaView(AdminModelView):
    
    form_widget_args = {
        'history': {
            'disabled': True
        }
    }

    @property
    def can_create(self):
        return current_user.has_permission('meta_add')

    @property
    def can_edit(self):
        return current_user.has_permission('meta_update')

    @property
    def can_delete(self):
        return False

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_permission('meta_read_all'))
        )

class AdminMetaHistoryView(AdminModelView):
    
    @property
    def can_create(self):
        return False

    @property
    def can_edit(self):
        return False

    @property
    def can_delete(self):
        return False

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_permission('meta_read_all'))
        )

class SecuredAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_role('superuser') or current_user.has_role('admin'))
        )

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))


class UserRolesView(BaseView):
    
    @expose('/')
    def index(self):
        data = models.User.query.all()
        roles = models.Role.query.order_by(models.Role.id).all()
        return self.render('admin/userroles.html', data=data, roles=roles)

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_permission('roles_manage'))

class ReassignForm(FlaskForm):
    current_user = SelectField('Current user')
    new_user = SelectField('New user')
    group = SelectField('Group')
    submit = SubmitField('Submit')

    def validate(self):
        if not super().validate():
            return False
        if request.form['destination'] == 'user':
            if self.current_user.data == self.new_user.data:
                self.new_user.errors.append("New user can't be the same as current user!")
                return False
        
        return True
    

class TaskReassignmentView(BaseView):

    @expose('/', methods = ['GET', 'POST'])
    def index(self):
        reassign_form = ReassignForm(request.form)
        user_choices = list()
        for user in models.User.query.order_by(models.User.name).all():
            user_choices.append((f'U_{user.username}', f'{user.name} <{user.email}>'))

        reassign_form.current_user.choices = user_choices
        reassign_form.new_user.choices  = user_choices

        group_choices = list()
        for group in models.Group.query.order_by(models.Group.name).all():
            group_choices.append((f'G_{group.groupname}', f'Group: {group.name} <{group.groupname}>'))
        reassign_form.group.choices = group_choices

        if reassign_form.validate_on_submit():
            old_user = get_object_from_arg(reassign_form.current_user.data[2:], models.User, models.User.username, skip_id=True)
                
            if request.form['destination'] == 'user':
                new_owner = get_object_from_arg(reassign_form.new_user.data[2:], models.User, models.User.username, skip_id=True)
                for task in old_user.tasks:
                    if task.status != 'done':
                        new_owner.user_tasks.append(task)
            elif request.form['destination'] == 'group':
                new_owner = get_object_from_arg(reassign_form.group.data[2:], models.Group, models.Group.groupname)
                for task in old_user.tasks:
                    if task.status != 'done':
                        new_user = distribute_task(group=new_owner)
                        new_user.user_tasks.append(task)
            
            # Remove reassigned tasks from the old user
            old_user.user_tasks = list(filter(lambda x: x.status == 'done', old_user.user_tasks))
            db.session.commit()

            return self.render('admin/reassignment_done.html', old_user=old_user, new_owner=new_owner)

        return self.render('admin/reassign.html', reassign_form=reassign_form)

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_permission('task_update_all')
        )

admin = Admin(name='Task Manager admin panel', template_mode='bootstrap4', index_view=SecuredAdminIndexView(url='/admin'))
admin.add_view(AdminTaskView(models.Task, db.session))
admin.add_view(AdminGroupView(models.Group, db.session))
admin.add_view(AdminUserView(models.User, db.session))
admin.add_view(UserRolesView(endpoint='/users/roles', name='User roles'))
admin.add_view(TaskReassignmentView(endpoint='/users/tasks', name='User tasks'))
admin.add_view(AdminMetaView(models.Meta, db.session))
admin.add_view(AdminMetaHistoryView(models.MetaHistory, db.session))
return_link = RightAlignedMenuLink(name='Return to main site', endpoint='web.index')
admin.add_link(return_link)