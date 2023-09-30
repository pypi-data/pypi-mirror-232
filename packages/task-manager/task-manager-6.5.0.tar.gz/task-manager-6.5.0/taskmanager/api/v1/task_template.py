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

import json

from flask import abort
from flask_restx import Resource, fields, reqparse
from flask_security import http_auth_required, permissions_accepted

from .base import api
from ... import models
from ...fields import ObjectUrl
from ...util.helpers import get_object_from_arg, json_type

db = models.db

task_template_get = api.model('TaskTemplateGet', {
    'uri': ObjectUrl('api_v1.task_template', attribute='label'),
    'label': fields.String,
    'content': fields.String,
})


task_template_post = api.model('TaskTemplatePost', {
    'label': fields.String,
    'content': fields.Raw,
})


task_template_list_get = api.model('TaskTemplateListGet', {
    'task_templates': fields.List(ObjectUrl('api_v1.task_template', attribute='label'))
})


@api.route('/task_templates', endpoint='task_templates')
class TaskTemplateListAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('label', type=str, required=True, location='json')
    request_parser.add_argument('content', type=json_type, required=True, location='json')

    @http_auth_required
    @permissions_accepted('task_read', 'task_read_all')
    @api.marshal_with(task_template_list_get)
    def get(self):
        task_templates = models.TaskTemplate.query.all()
        return {'task_templates': task_templates}

    @http_auth_required
    @permissions_accepted('template_add')
    @api.marshal_with(task_template_get)
    @api.expect(task_template_post)
    @api.response(201, "Create task template")
    def post(self):
        arguments = self.request_parser.parse_args()
        label = arguments['label']
        content = arguments['content']

        if not isinstance(content, str):
            content = json.dumps(content)

        task_template = models.TaskTemplate(label=label, content=content)
        db.session.add(task_template)
        db.session.commit()

        # Refresh the task object before returning
        db.session.refresh(task_template)
        return task_template, 201


@api.route('/task_templates/<id>', endpoint='task_template')
class TaskTemplateAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('label', type=str, required=False, location='json')
    request_parser.add_argument('content', type=json_type, required=False, location='json')

    @http_auth_required
    @permissions_accepted('task_read', 'task_read_all')
    @api.marshal_with(task_template_get)
    @api.response(200, "Success")
    @api.response(404, "Could not find task template")
    def get(self, id):
        task_template = get_object_from_arg(id, models.TaskTemplate, models.TaskTemplate.label)

        if task_template is None:
            abort(404)

        return task_template

    @http_auth_required
    @permissions_accepted('template_update')
    @api.marshal_with(task_template_get)
    @api.response(200, "Success")
    @api.response(404, "Could not find task template")
    @api.expect(task_template_post)
    def put(self, id):
        task_template = get_object_from_arg(id, models.TaskTemplate, models.TaskTemplate.label)
        if task_template is None:
            abort(404)

        args = self.request_parser.parse_args()

        if args['label'] is not None:
            task_template.label = args['label']

        if args['content'] is not None:
            content = args['content']
            print(f'Found content: [{type(content).__name__}] {content}')

            if not isinstance(content, str):
                content = json.dumps(content)

            task_template.content = content

        db.session.commit()
        db.session.refresh(task_template)
        return task_template

    @http_auth_required
    @permissions_accepted('template_delete')
    @api.response(200, "Success")
    @api.response(404, "Could not find task template")
    def delete(self, id):
        task_template = get_object_from_arg(id, models.TaskTemplate, models.TaskTemplate.label)
        if task_template is None:
            abort(404)

        db.session.delete(task_template)
        db.session.commit()

