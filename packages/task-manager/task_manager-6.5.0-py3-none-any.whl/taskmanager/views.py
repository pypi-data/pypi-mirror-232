# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import abort
from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_restx import reqparse
from flask_security import current_user
from flask_security import login_required
from flask_security import permissions_required
from flask_security import permissions_accepted
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired

from . import control, models
from .util.mail import send_bulk_mail
from .util.helpers import get_object_from_arg

# Create the web blueprint
bp = Blueprint('web', __name__)


@bp.app_errorhandler(404)
def page_not_found_error(error):
    title = f'Taskmanager: 404 Not Found'
    return render_template('error/notfound.html', title=title), 404


@bp.errorhandler(403)
def forbidden_error(error):
    title = f'Taskmanager: 403 Forbidden'
    return render_template('error/forbidden.html', title=title), 404


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/tasks')
@login_required
@permissions_accepted('task_read', 'task_read_all')
def tasks():
    get_request_parser = reqparse.RequestParser()
    get_request_parser.add_argument('project', type=str, required=False, location='args', help="Filter on project name")
    get_request_parser.add_argument('template', type=str, required=False, location='args', help="Filter on template label")
    get_request_parser.add_argument('user', type=str, required=False, location='args', help="Filter on user by id or label")
    get_request_parser.add_argument('status', type=str, required=False, location='args', help="Filter on status.")
    get_request_parser.add_argument('tag', type=str, action='append', required=False, location='args', help="Tag name or list of tag names to filter on. When multiple tag args are given AND filter logic is applied.")
    get_request_parser.add_argument('application_name', type=str, required=False, location='args', help="Filter on application name")
    get_request_parser.add_argument('offset', type=int, required=False, location='args', help="Offset for pagination")
    get_request_parser.add_argument('limit', type=int, required=False, location='args', help="Maximum number of rows returned")

    args = get_request_parser.parse_args()

    offset = args['offset'] or 0
    limit = args['limit'] or 25

    tasks, total_nr_of_tasks = control.query_tasks(
        user=args['user'] or False,  # Signal no filter if user not set
        project=args['project'],
        status=args['status'],
        template=args['template'],
        tags=args['tag'],
        application_name=args['application_name'],
        offset=offset,
        limit=limit,
        order='asc',
    )

    return render_template('tasks.html', data=tasks, offset=offset, limit=limit, total=total_nr_of_tasks)


@bp.route('/tasks/<int:id>')
@login_required
@permissions_accepted('task_read', 'task_read_all')
def task(id):
    query = models.Task.query.filter(models.Task.id == id)
    if not current_user.has_permission('task_read_all'):
        tasks_via_user_query = query.filter(models.Task.users.contains(current_user))
        tasks_via_group_query = query.filter(models.Task.users_via_group.contains(current_user))
        query = tasks_via_user_query.union(tasks_via_group_query)
    data = query.one_or_none()

    if data is None:
        abort(404)

    return render_template('task.html', data=data)


@bp.route('/taskgroups')
@login_required
@permissions_accepted('task_read', 'task_read_all')
def taskgroups():
    data = models.TaskGroup.query.order_by(models.TaskGroup.id.asc()).all()
    if data is None:
        abort(404)
    return render_template('taskgroups.html', data=data)


@bp.route('/taskgroups/<int:id>')
@login_required
@permissions_accepted('task_read', 'task_read_all')
def taskgroup(id):
    data = models.TaskGroup.query.filter(models.TaskGroup.id == id).one_or_none()
    if data is None:
        abort(404)
    return render_template('taskgroup.html', data=data)


@bp.route('/templates')
@login_required
def templates():
    data = models.TaskTemplate.query.all()
    return render_template('templates.html', data=data)


@bp.route('/templates/<int:id>')
@login_required
def template(id):
    data = models.TaskTemplate.query.filter(models.TaskTemplate.id == id).one_or_none()

    # Count the tasks per template for this user
    users = models.User.query.all()

    counts_per_user = []
    for user in users:
        tasks_via_user_query = models.Task.query.filter(models.Task.users.contains(user))
        tasks_via_group_query = models.Task.query.filter(models.Task.users_via_group.contains(user))
        all_tasks_query = tasks_via_user_query.union(tasks_via_group_query)
        template_query = all_tasks_query.filter(models.Task.template == data)

        count_data = {
            'user_id': user.id,
            'user': user.username,
            'tasks': template_query.count(),
            'tasks_queued': template_query.filter(models.Task._status == 'queued').count(),
        }
        if count_data['tasks'] > 0:
            counts_per_user.append(count_data)

    if data is None:
        abort(404)
    return render_template('template.html', data=data, counts_per_user=counts_per_user)


@bp.route('/users')
@login_required
@permissions_accepted('user_read_all')
def users():
    data = models.User.query.all()

    return render_template('users.html', data=data)


@bp.route('/users/<int:id>')
@login_required
@permissions_accepted('user_read', 'user_read_all')
def user(id):
    data = models.User.query.filter(models.User.id == id).one_or_none()
    if data is None:
        abort(404)

    if not current_user.has_permission('user_read_all'):
        # This is a normal user, so may only see own user information.
        if current_user != data:
            abort(403)

    # Count the tasks per template for this user
    templates = models.TaskTemplate.query.all()

    tasks_via_user_query = models.Task.query.filter(models.Task.users.contains(data))
    tasks_via_group_query = models.Task.query.filter(models.Task.users_via_group.contains(data))
    all_tasks_query = tasks_via_user_query.union(tasks_via_group_query)

    counts_per_template = []
    for template in templates:
        template_query = all_tasks_query.filter(models.Task.template == template)
        count_data = {
            'template_id': template.id,
            'template': template.label,
            'tasks': template_query.count(),
            'tasks_queued': template_query.filter(models.Task._status == 'queued').count(),
        }
        if count_data['tasks'] > 0:
            counts_per_template.append(count_data)

    return render_template('user.html', data=data, counts_per_template=counts_per_template)


@bp.route('/groups')
@login_required
@permissions_accepted('group_read_all')
def groups():
    data = models.Group.query.all()
    return render_template('groups.html', data=data)


@bp.route('/groups/<int:id>')
@login_required
@permissions_accepted('group_read', 'group_read_all')
def group(id):
    data = models.Group.query.filter(models.Group.id == id).one_or_none()
    if data is None:
        abort(404)

    if not current_user.has_permission('group_read_all'):
        if data not in current_user.groups:
            abort(403)

    return render_template('group.html', data=data)


@bp.route('/tags')
@login_required
@permissions_accepted('task_read', 'task_read_all')
def tags():
    data = models.Tag.query.order_by(models.Tag.id).all()
    return render_template('tags.html', data=data)


@bp.route('/tags/<int:id>')
@login_required
@permissions_accepted('task_read_all')
def tag(id):
    data = models.Tag.query.filter(models.Tag.id == id).one_or_none()
    if data is None:
        abort(404)

    return render_template('tag.html', data=data)


class MailForm(FlaskForm):
    recipients = SelectMultipleField('Recipients')
    subject = StringField('Subject', validators=[DataRequired()])
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

    @bp.route("/mail", methods=['GET', 'POST'])
    @login_required
    @permissions_accepted('user_read_all')
    def mail():
        form = MailForm(request.form)

        choices = [('A_all', 'All users')]

        for group in models.Group.query.order_by(models.Group.name).all():
            choices.append((f'G_{group.groupname}', f'Group: {group.name} <{group.groupname}>'))

        for user in models.User.query.order_by(models.User.name).all():
            choices.append((f'U_{user.username}', f'{user.name} <{user.email}>'))

        form.recipients.choices = choices

        if form.validate_on_submit():
            recipients = form.recipients.data
            subject = form.subject.data
            body = form.body.data

            new_recipients = set()
            for recipient in recipients:
                if recipient.startswith('A_'):
                    for user in models.User.query.all():
                        new_recipients.add(user)
                elif recipient.startswith('G_'):
                    group = get_object_from_arg(recipient[2:], models.Group, models.Group.groupname, skip_id=True)
                    for user in group.users:
                        new_recipients.add(user)
                elif recipient.startswith('U_'):
                    user = get_object_from_arg(recipient[2:], models.User, models.User.username, skip_id=True)
                    new_recipients.add(user)

            recipients = sorted(new_recipients, key=lambda u: u.username)

            send_bulk_mail(
                recipients=recipients,
                subject=subject,
                body=body,
            )
            return render_template('mail_sent.html',
                                   recipients=recipients,
                                   subject=subject,
                                   body=body)

        return render_template('mail.html', mail_form=form)


class TaskReassignment(FlaskForm):
    original_user = SelectField('Tasks assigned to:', validators=[DataRequired()])
    new_user = SelectField('New user:')
    new_user_group = SelectField('New user group:')
    submit = SubmitField('Reassign')
    
    def validate(self, extra_validators=None):
        if self.new_user.data == 'N_None' and self.new_user_group.data == 'N_None':
            self.new_user.errors.append("Select either a new user or a new user group to reassign tasks to.")
            return False
        elif (self.new_user.data != 'N_None') and (self.new_user_group.data != 'N_None'):
            self.new_user.errors.append("You have selected both the new user and the new user group. Choose one.")
            return False
        return super().validate()

    @bp.route("/admin/tasks/reassign", methods=['GET', 'POST'])
    @login_required
    @permissions_required('user_read_all', 'task_update_all')
    def reassign():
        form = TaskReassignment(request.form)
        
        group_choices = [('N_None', '')]
        new_user_choices = [('N_None', '')]
        user_choices = []
        for group in models.Group.query.order_by(models.Group.name).all():
            group_choices.append((f'G_{group.groupname}', f'Group: {group.name} <{group.groupname}>'))

        for user in models.User.query.order_by(models.User.name).all():
            user_choices.append((f'U_{user.username}', f'{user.name} <{user.email}>'))
            if user.active:
                new_user_choices.append((f'U_{user.username}', f'{user.name} <{user.email}>'))

        form.new_user_group.choices = group_choices
        form.new_user.choices = new_user_choices
        form.original_user.choices = user_choices

        if form.validate_on_submit():
            old_user = models.User.query.filter(models.User.username == form.original_user.data[2:]).one()
            # Only reassign queued tasks
            tasks_to_reassign = [task for task in old_user.user_tasks if task.status == 'queued']
            if form.new_user.data != 'N_None':
                destination = models.User.query.filter(models.User.username == form.new_user.data[2:]).one()
                destination.user_tasks.extend(tasks_to_reassign)
                template_destination = ("user", destination.username)
            else:
                destination = models.Group.query.filter(models.Group.groupname == form.new_user_group.data[2:]).one()
                destination.tasks.extend(tasks_to_reassign)                
                template_destination = ("group", destination.groupname)
            # Keep other tasks assigned to the old user
            old_user.user_tasks = [task for task in old_user.user_tasks if task.status != 'queued']
            models.db.session.commit()
            return render_template('admin/tasks_reassigned.html', user=old_user, destination=template_destination, reassigned_tasks=tasks_to_reassign)

        return render_template('admin/task_reassignment.html', reassign_form=form)