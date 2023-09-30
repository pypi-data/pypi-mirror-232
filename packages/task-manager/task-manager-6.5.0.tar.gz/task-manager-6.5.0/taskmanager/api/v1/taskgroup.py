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

from flask_restx import fields, Resource, reqparse
from flask_security import http_auth_required, permissions_accepted

from .base import api
from .task import task_summary, task_post
from ... import models, control, exceptions
from ...fields import ObjectUrl
from ...util.helpers import get_object_from_arg

db = models.db

taskgroup = api.model(
    'TaskGroupGet',
    {
        'url': ObjectUrl('api_v1.taskgroup', attribute='id'),
        'id': fields.String,
        'label': fields.String,
        'status': fields.String,
        'callback_url': fields.String,
        'callback_content': fields.String,
        'tasks': fields.List(
            fields.Nested(task_summary)
        )
    }
)

taskgroup_list_post = api.model(
    'TaskGroupPost',
    {
        'label': fields.String,
        'callback_url': fields.String,
        'callback_content': fields.String,
        'distribute_in_group': fields.String,
        'distribute_method': fields.String,
        'tasks': fields.List(
            fields.Nested(task_post)
        )
    }
)

taskgroup_list_get = api.model('TaskGroupListGet', {
    'taskgroups': fields.List(
        fields.Nested(
            api.model('TaskgroupSummary',
                      {
                          'url': ObjectUrl('api_v1.taskgroup', attribute='id'),
                          'id': fields.String,
                          'label': fields.String,
                          'status': fields.String,
                      }
            )
        )
    )
})


@api.route('/taskgroups', endpoint='taskgroups')
class TaskGroupListAPI(Resource):
    get_request_parser = reqparse.RequestParser()
    get_request_parser.add_argument('status', type=str, required=False, location='args')

    post_request_parser = reqparse.RequestParser()
    post_request_parser.add_argument('label', type=str, required=True, location='json')
    post_request_parser.add_argument('callback_url', type=str, required=True, location='json')
    post_request_parser.add_argument('callback_content', type=str, required=True, location='json')
    post_request_parser.add_argument('tasks', type=list, required=True, location='json')
    post_request_parser.add_argument('distribute_in_group', type=str, required=False, location='json')
    post_request_parser.add_argument('distribute_method', type=str, required=False, location='json')

    @http_auth_required
    @permissions_accepted('task_read', 'task_read_all')
    @api.marshal_with(taskgroup_list_get)
    @api.expect(get_request_parser)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find user or template')
    def get(self):
        args = self.get_request_parser.parse_args()
        status = args['status']

        taskgroups = models.TaskGroup.query.all()

        if status is not None:
            taskgroups = [x for x in taskgroups if x.status == status]

        return {'taskgroups': taskgroups}

    @http_auth_required
    @permissions_accepted('task_add', 'task_update_all')
    @api.marshal_with(taskgroup)
    @api.expect(taskgroup_list_post)
    @api.response(201, 'Created')
    @api.response(404, 'Could not find a required resource')
    def post(self):
        args = self.post_request_parser.parse_args()
        label = args['label']
        callback_url = args['callback_url']
        callback_content = args['callback_content']
        distribute_in_group = args['distribute_in_group']
        distribute_method = args['distribute_method']
        tasks = args['tasks']

        try:
            taskgroup = control.insert_taskgroup(label=label,
                                                 callback_url=callback_url,
                                                 callback_content=callback_content,
                                                 distribute_in_group=distribute_in_group,
                                                 distribute_method=distribute_method,
                                                 tasks=tasks)
        except exceptions.TaskManagerError:
            db.session.rollback()
            raise

        # Commit and return
        db.session.commit()
        db.session.refresh(taskgroup)
        return taskgroup, 201


taskgroup_put = api.model(
    'TaskGroupGet',
    {
        'label': fields.String,
        'callback_url': fields.String,
        'callback_content': fields.String,
        'tasks': fields.List(fields.Integer)
    }
)

@api.route('/taskgroups/<id>', endpoint='taskgroup')
class TaskGroupAPI(Resource):
    put_request_parser = reqparse.RequestParser()
    put_request_parser.add_argument('label', type=str, required=False, location='json')
    put_request_parser.add_argument('callback_url', type=str, required=False, location='json')
    put_request_parser.add_argument('callback_content', type=str, required=False, location='json')
    put_request_parser.add_argument('tasks', type=list, required=False, location='json')

    @http_auth_required
    @permissions_accepted('task_read', 'task_read_all')
    @api.marshal_with(taskgroup)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find selected taskgroup')
    def get(self, id):
        return get_object_from_arg(id, models.TaskGroup, models.TaskGroup.label)

    @http_auth_required
    @permissions_accepted('task_add', 'task_update_all')
    @api.marshal_with(taskgroup)
    @api.expect(taskgroup_put)
    @api.response(200, 'Success')
    @api.response(404, 'Taskgroup or child task not found')
    def put(self, id):
        args = self.put_request_parser.parse_args()
        taskgroup = get_object_from_arg(id, models.TaskGroup, models.TaskGroup.label)

        # Unpack arguments
        label = args['label']
        callback_url = args['callback_url']
        callback_content = args['callback_content']
        tasks = args['tasks']

        if label is not None:
            taskgroup.label = label

        if callback_url is not None:
            taskgroup.callback_url = callback_url

        if callback_content is not None:
            taskgroup.callback_content = callback_content

        if tasks is not None:
            tasks = [get_object_from_arg(x, models.Task) for x in tasks]
            taskgroup.tasks = tasks

        db.session.commit()
        db.session.refresh(taskgroup)
        return taskgroup
