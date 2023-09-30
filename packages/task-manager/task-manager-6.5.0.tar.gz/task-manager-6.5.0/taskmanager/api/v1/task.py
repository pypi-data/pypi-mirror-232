# Copyright 2017-2021 Biomedical Imaging Group Rotterdam, Departments of
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

from datetime import datetime
from flask import abort
from flask_restx import fields, inputs, Resource, reqparse
from flask_security import current_user, http_auth_required, permissions_accepted, permissions_required
from string import Template

from .base import api
from .tag import tag_summary
from ... import control, models, db, exceptions
from ...fields import ObjectUrl, SubUrl
from ...util.helpers import get_object_from_arg, json_type, list_of_int_or_str, has_permission_any

task_summary = api.model('TaskSummary',
          {
              'uri': ObjectUrl('api_v1.task', attribute='id'),
              'id': fields.String,
              'status': fields.String,
              'project': fields.String,
              'template': ObjectUrl('api_v1.task_template', attribute='template_id'),
              'tags': fields.List(fields.Nested(tag_summary))
          }
)


task_list_get = api.model('TaskListGet', {
    'tasks': fields.List(fields.Nested(task_summary)),
    'total_tasks': fields.Integer,
    'limit': fields.Integer,
    'offset': fields.Integer,

})

task_get = api.model('TaskGet', {
    'uri': fields.Url('api_v1.task'),
    'project': fields.String,
    'template': ObjectUrl('api_v1.task_template', attribute='template_id'),
    'content': fields.String,
    'status': fields.String,
    'lock': SubUrl('api_v1.task', 'lock', attribute='id'),
    'tags': fields.List(ObjectUrl('api_v1.tag', attribute='id')),
    'callback_url': fields.String,
    'callback_content': fields.String,
    'generator_url': fields.String,
    'application_name': fields.String,
    'application_version': fields.String,
    'create_time': fields.DateTime,
    'update_time': fields.DateTime,
    'users': fields.List(ObjectUrl('api_v1.user', attribute='id')),
    'groups': fields.List(ObjectUrl('api_v1.group', attribute='id')),
    'users_via_group': fields.List(ObjectUrl('api_v1.user', attribute='id')),
})


task_post = api.model('TaskPost', {
    'project': fields.String,
    'template': fields.String,
    'content': fields.String,
    'raw_content': fields.String,
    'tags': fields.List(ObjectUrl('api_v1.tag', attribute='id')),
    'callback_url': fields.String,
    'raw_callback_url': fields.String,
    'callback_content': fields.String,
    'generator_url': fields.String,
    'tracking_id': fields.String,
    'application_name': fields.String,
    'application_version': fields.String,
    'users': fields.List(ObjectUrl('api_v1.user', attribute='id')),
    'groups': fields.List(ObjectUrl('api_v1.group', attribute='id')),
    'distribute_in_group': fields.String,
})


task_put = api.model('TaskPut', {
    'project': fields.String,
    'template': fields.String,
    'content': fields.String,
    'raw_content': fields.String,
    'status': fields.String,
    'raw_callback_url': fields.String,
    'callback_url': fields.String,
    'callback_content': fields.String,
    'generator_url': fields.String,
    'tracking_id': fields.String,
    'application_name': fields.String,
    'application_version': fields.String,
    'tags': fields.List(ObjectUrl('api_v1.tag', attribute='id')),
    'users': fields.List(ObjectUrl('api_v1.user', attribute='id')),
    'groups': fields.List(ObjectUrl('api_v1.group', attribute='id')),
})


@api.route('/tasks', endpoint='tasks')
class TaskListAPI(Resource):
    get_request_parser = reqparse.RequestParser()
    get_request_parser.add_argument('project', type=str, required=False, location='args', help="Filter on project name")
    get_request_parser.add_argument('template', type=str, required=False, location='args', help="Filter on template label")
    get_request_parser.add_argument('user', type=str, required=False, location='args', help="Filter on user by id or label")
    get_request_parser.add_argument('status', type=str, required=False, location='args', help="Filter on status.")
    get_request_parser.add_argument('tag', type=str, action='append', required=False, location='args', help="Tag name or list of tag names to filter on. When multiple tag args are given AND filter logic is applied.")
    get_request_parser.add_argument('application_name', type=str, required=False, location='args', help="Filter on application name")
    get_request_parser.add_argument('offset', type=int, required=False, location='args', help="Offset for pagination")
    get_request_parser.add_argument('limit', type=int, required=False, location='args', help="Maximum number of rows returned")

    post_request_parser = reqparse.RequestParser()
    post_request_parser.add_argument('project', type=str, required=True, location='json')
    post_request_parser.add_argument('template', type=str, required=True, location='json')
    post_request_parser.add_argument('content', type=json_type, required=True, location='json')
    post_request_parser.add_argument('raw_content', type=str, required=False, location='json')
    post_request_parser.add_argument('callback_url', type=str, required=False, location='json')
    post_request_parser.add_argument('raw_callback_url', type=str, required=False, location='json')
    post_request_parser.add_argument('callback_content', type=str, required=False, location='json')
    post_request_parser.add_argument('generator_url', type=str, required=False, location='json')
    post_request_parser.add_argument('tracking_id', type=str, required=False, location='json')
    post_request_parser.add_argument('application_name', type=str, required=False, location='json')
    post_request_parser.add_argument('application_version', type=str, required=False, location='json')
    post_request_parser.add_argument('tags', type=list, required=False, location='json')
    post_request_parser.add_argument('users', type=list_of_int_or_str, required=False, location='json')
    post_request_parser.add_argument('groups', type=list_of_int_or_str, required=False, location='json')
    post_request_parser.add_argument('distribute_in_group', type=str, required=False, location='json')

    @http_auth_required
    @permissions_accepted('task_read', 'task_read_all')
    @api.marshal_with(task_list_get)
    @api.expect(get_request_parser)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find user or template')
    def get(self):
        args = self.get_request_parser.parse_args()
        offset = args['offset']
        limit = args['limit']

        tasks, total_nr_of_tasks = control.query_tasks(
            user=args['user'],
            project=args['project'],
            status=args['status'],
            template=args['template'],
            tags=args['tag'],
            application_name=args['application_name'],
            offset=offset,
            limit=limit,
        )

        return {
            'tasks': tasks,
            'offset': offset,
            'limit': limit,
            'count': total_nr_of_tasks,
        }

    @http_auth_required
    @permissions_required('task_add')
    @api.marshal_with(task_get)
    @api.expect(task_post)
    @api.response(201, 'Created new task')
    @api.response(400, 'Invalid request: specified both users/groups and a distribute in group directive')
    @api.response(404, 'Could not find all users, groups or template')
    def post(self):
        args = self.post_request_parser.parse_args()

        try:
            task = control.insert_task(
                content=args['content'],
                raw_content = args['raw_content'],
                project=args['project'],
                callback_url=args['callback_url'],
                raw_callback_url=args['raw_callback_url'],
                callback_content=args['callback_content'],
                template=args['template'],
                tracking_id=args['tracking_id'],
                generator_url=args['generator_url'],
                tags=args['tags'],
                users=args['users'],
                groups=args['groups'],
                distribute_in_group=args['distribute_in_group'],
                application_name=args['application_name'],
                application_version=args['application_version'],
            )
        except exceptions.TaskManagerError:
            db.session.rollback()
            raise

        # Commit changes to db
        print(f'Task.users {task.users}')
        print(f'Task.groups {task.groups}')
        db.session.commit()

        # Refresh the task object before returning
        db.session.refresh(task)
        return task, 201


@api.route('/tasks/<int:id>', endpoint='task')
class TaskAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('project', type=str, required=False, location='json')
    request_parser.add_argument('template', type=str, required=False, location='json')
    request_parser.add_argument('content', type=json_type, required=False, location='json')
    request_parser.add_argument('raw_content', type=str, required=False, location='json')
    request_parser.add_argument('status', type=str, required=False, location='json')
    request_parser.add_argument('callback_url', type=str, required=False, location='json')
    request_parser.add_argument('raw_callback_url', type=str, required=False, location='json')
    request_parser.add_argument('callback_content', type=str, required=False, location='json')
    request_parser.add_argument('generator_url', type=str, required=False, location='json')
    request_parser.add_argument('application_name', type=str, required=False, location='json')
    request_parser.add_argument('application_version', type=str, required=False, location='json')
    request_parser.add_argument('tags', type=list, required=False, location='json')
    request_parser.add_argument('users', type=list_of_int_or_str, required=False, location='json')
    request_parser.add_argument('groups', type=list_of_int_or_str, required=False, location='json')

    @http_auth_required
    @permissions_accepted('task_read', 'task_read_all')
    @api.marshal_with(task_get)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find selected task')
    def get(self, id):
        query = models.Task.query.filter(models.Task.id == id)

        if not current_user.has_permission('task_read_all'):
            tasks_via_user_query = query.filter(models.Task.users.contains(current_user))
            tasks_via_group_query = query.filter(models.Task.users_via_group.contains(current_user))
            query = tasks_via_user_query.union(tasks_via_group_query)
        task = query.one_or_none()

        if task is None:
            abort(404)

        return task

    @http_auth_required
    @permissions_accepted('task_update_status', 'task_update_status_all', 'task_update_user', 'task_update_all')
    @api.marshal_with(task_get)
    @api.expect(task_put)
    @api.response(200, 'Success')
    @api.response(403, 'You are not authorized to perform this operation')
    @api.response(404, 'Could not find selected task, user(s), group(s) or template')
    def put(self, id):
        query = models.Task.query.filter(models.Task.id == id)

        # Check if the current may change the status of all tasks or has task 
        # update super powers. If not limit to current_user assigned tasks only.
        if not has_permission_any('task_update_status_all', 'task_update_all'):
            tasks_via_user_query = query.filter(models.Task.users.contains(current_user))
            tasks_via_group_query = query.filter(models.Task.users_via_group.contains(current_user))
            query = tasks_via_user_query.union(tasks_via_group_query)
        task = query.one_or_none()
        
        if task is None:
            abort(404, 'Could not find selected task')

        args = self.request_parser.parse_args()

        if args['project'] is not None:
            if has_permission_any('task_update_all'):
                task.project = args['project']
            else:
                abort(403, "You are not authorized to update the project name")


        if args['template'] is not None:
            if has_permission_any('task_update_all'):
                try:
                    template = get_object_from_arg(args['template'],
                                                models.TaskTemplate,
                                                models.TaskTemplate.label)
                except exceptions.TaskManagerError as exception:
                    abort(exception.default_http_status, str(exception))

                task.template = template
            else:
                abort(403, "You are not authorized to update the template")


        if args['content'] is not None:
            if has_permission_any('task_update_all'):
                content = args['content']

                if not isinstance(content, str):
                    content = json.dumps(content)

                if args['raw_content'] is None:
                    task.raw_content = content
            else:
                abort(403, "You are not authorized to update the content")
        
        if args['raw_content'] is not None:
            if has_permission_any('task_update_all'):
                task.raw_content = args['raw_content']
            else:
                abort(403, "You are not authorized to update the content")

        if args['status'] is not None:
            if has_permission_any('task_update_status', 'task_update_status_all', 'task_update_all'):
                task.status = args['status']
            else:
                abort(403, "You are not authorized to update the status")


        if args['callback_url'] is not None:
            if has_permission_any('task_update_all'):
                if args['raw_callback_url'] is None:
                    task.raw_callback_url = args['callback_url']
            else:
                abort(403, "You are not authorized to update the callback url")

        if args['raw_callback_url'] is not None:
            if has_permission_any('task_update_all'):
                task.raw_callback_url = args['raw_callback_url']
            else:
                abort(403, "You are not authorized to update the callback url")

        if args['callback_content'] is not None:
            if has_permission_any('task_update_all'):
                task.callback_content = args['callback_content']
            else:
                abort(403, "You are not authorized to update the callback content")

        if args['generator_url'] is not None:
            if has_permission_any('task_update_all'):
                task.generator_url = args['generator_url']
            else:
                abort(403, "You are not authorized to update the generator url")

        if args['application_name'] is not None:
            if has_permission_any('task_update_all'):
                task.application_name = args['application_name']
            else:
                abort(403, "You are not authorized to update the application name")

        if args['application_version'] is not None:
            if has_permission_any('task_update_all'):
                task.application_version = args['application_version']
            else:
                abort(403, "You are not authorized to update the application version")

        # Add tags
        if args['tags'] is not None:
            if has_permission_any('task_update_all'):
                tags = []
                for tag in args['tags']:
                    if isinstance(tag, int):
                        tag_object = models.Tag.query.filter(models.Tag.id == tag).one_or_none()
                    else:
                        tag_object = models.Tag.query.filter(models.Tag.name == tag).one_or_none()

                    if tag_object is None:
                        print(f'Adding tag {tag}')
                        tag_object = models.Tag(tag)
                        db.session.add(tag_object)
                    else:
                        print(f'Reusing tag {tag}')

                    tags.append(tag_object)

                # Set the tags in one go (overwriting all old tags)
                task.tags = tags
            else:
                abort(403, "You are not authorized to update the tags")


        # Set users
        if args['users'] is not None:
            if has_permission_any('task_update_user', 'task_update_all'):
                users = []
                for user in args['users']:
                    if isinstance(user, int):
                        user_object = models.User.query.filter(models.User.id == user).one_or_none()
                    else:
                        user_object = models.User.query.filter(models.User.username == user).one_or_none()

                    if user_object is None:
                        abort(404, f"Could not find all users (user {user} not found)")

                    users.append(user_object)

                task.users = users
            else:
                abort(403, "You are not authorized to update the users")


        # Set groups
        if args['groups'] is not None:
            if has_permission_any('task_update_user', 'task_update_all'):
                groups = []
                for group in args['groups']:
                    if isinstance(group, int):
                        group_object = models.Group.query.filter(models.Group.id == group).one_or_none()
                    else:
                        group_object = models.Group.query.filter(models.Group.groupname == group).one_or_none()

                    if group_object is None:
                        abort(404, f"Could not find all groups (group {group} not found)")

                    groups.append(group_object)

                task.groups = groups
            else:
                abort(403, "You are not authorized to update the groups")

        db.session.commit()
        db.session.refresh(task)

        return task

    @http_auth_required
    @permissions_accepted('task_delete')
    @api.response(200, "Success")
    @api.response(404, "Could not find task")
    def delete(self, id):
        task = models.Task.query.filter(models.Task.id == id).one_or_none()

        if task is None:
            abort(404)
        
        db.session.delete(task)
        db.session.commit()
        

@api.route('/task-at-timepoint/<int:id>', endpoint='task-at-timepoint')
class TaskAtTimepointAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('timestamp', type=inputs.datetime_from_iso8601, required=False, default=datetime.now(), location='args', help="Date and time on which you'd like to calculate the task contents (ISO8601)")
    
    @http_auth_required
    @permissions_accepted('task_read', 'task_read_all')
    @api.marshal_with(task_get)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find selected task')
    def get(self, id):
        args = self.request_parser.parse_args()
        filter_timestamp = args['timestamp']
        
        query = models.Task.query.filter(models.Task.id == id)

        if not current_user.has_permission('task_read_all'):
            tasks_via_user_query = query.filter(models.Task.users.contains(current_user))
            tasks_via_group_query = query.filter(models.Task.users_via_group.contains(current_user))
            query = tasks_via_user_query.union(tasks_via_group_query)
        task = query.one_or_none()

        if task is None:
            abort(404)
        
        # Find meta history entries with latest values before requested timestamp
        latest_timestamps = db.session.query(models.MetaHistory.meta_id, func.max(models.MetaHistory.timestamp).label("maxtimestamp")).filter(models.MetaHistory.timestamp<filter_timestamp).group_by(models.MetaHistory.meta_id).subquery()

        # Find values for corresponding entries and join with labels.
        latest_meta = db.session.query(models.Meta.label, latest_timestamps.c.meta_id, models.MetaHistory.value).join(models.MetaHistory, (latest_timestamps.c.meta_id==models.MetaHistory.meta_id) & (latest_timestamps.c.maxtimestamp==models.MetaHistory.timestamp)).join(models.Meta, latest_timestamps.c.meta_id==models.Meta.id).all()

        mapping = {obj.label: obj.value for obj in latest_meta}

        content_template = Template(task.raw_content)
        callback_template = Template(task.raw_callback_url)
        
        task.content = None if task.raw_content is None else content_template.safe_substitute(**mapping)
        task.callback_url = None if task.raw_callback_url is None else callback_template.safe_substitute(**mapping)

        return task

@api.route('/tags/<int:id>/tasks', endpoint='tagtasks')
class TagTaskListAPI(Resource):
    @http_auth_required
    @permissions_accepted('task_read', 'task_read_all')
    @api.marshal_with(task_list_get)
    @api.response(200, "Succes")
    @api.response(404, "Could not find tag")
    def get(self, id):
        tag = models.Tag.query.filter(models.Tag.id == id).one_or_none()

        if tag is None:
            abort(404)
        
        return {'tasks': tag.tasks}
