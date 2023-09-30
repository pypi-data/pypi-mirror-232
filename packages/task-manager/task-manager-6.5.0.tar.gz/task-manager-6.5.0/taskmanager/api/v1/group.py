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


from flask import abort
from flask_restx import fields, reqparse, Resource
from flask_security import http_auth_required, permissions_accepted, current_user, permissions_required

from .base import api
from .user import user_list_get
from ... import models, db
from ...fields import ObjectUrl, SubUrl
from ...util.helpers import has_permission_any, has_permission_all


group_list_get = api.model("GroupListGet", {
    'groups': fields.List(ObjectUrl('api_v1.group', attribute='id'))
})


group_get = api.model("GroupGet", {
    'groupname': fields.String,
    'uri': fields.Url('api_v1.group'),
    'name': fields.String,
    'create_time': fields.DateTime,
    'tasks': SubUrl('api_v1.group', 'tasks', attribute='id'),
    'users': SubUrl('api_v1.group', 'users', attribute='id'),
})


group_put = api.model("GroupPut", {
    'groupname': fields.String,
    'name': fields.String,
})


@api.route('/users/<id>/groups', endpoint='usergroups')
class UserGroupListAPI(Resource):
    @http_auth_required
    @permissions_accepted('user_read', 'user_read_all')
    @api.marshal_with(group_list_get)
    @api.response(200, "Success")
    @api.response(403, "You are not authorized to get this information")
    @api.response(404, "User not found")
    def get(self, id):
        user = models.User.query.filter(models.User.id == id).one_or_none()

        if not has_permission_any('user_read_all'):
            if user != current_user:
                abort(403, "You are not authorized to get this information")

        if user is None:
            abort(404)
        
        return {'groups': user.groups}


@api.route('/groups', endpoint='groups')
class GroupListAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('groupname', type=str, required=True, location='json')
    request_parser.add_argument('name', type=str, required=False, location='json')

    @http_auth_required
    @permissions_accepted('group_read_all')
    @api.marshal_with(group_list_get)
    def get(self):
        groups = models.Group.query.all()
        return {"groups": groups}

    @http_auth_required
    @permissions_accepted('group_add')
    @api.marshal_with(group_get)
    @api.expect(group_put)
    @api.response(201, "Created group")
    def post(self):
        args = self.request_parser.parse_args()
        if args['name'] is None:
            args['name'] = args['groupname']

        group = models.Group(**args)
        db.session.add(group)
        db.session.commit()
        db.session.refresh(group)
        return group, 201


@api.route('/groups/<id>', endpoint='group')
class GroupAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('groupname', type=str, required=False, location='json')
    request_parser.add_argument('name', type=str, required=False, location='json')

    @http_auth_required
    @permissions_accepted('group_read', 'group_read_all')
    @api.marshal_with(group_get)
    @api.response(200, "Success")
    @api.response(404, "Could not find group")
    def get(self, id):
        group = models.Group.query.filter(models.Group.id == id).one_or_none()

        if group is None:
            abort(404)

        if not has_permission_all('group_read_all'):
            if group not in current_user.groups:
                abort(403)

        return group

    @http_auth_required
    @permissions_accepted('group_update')
    @api.marshal_with(group_get)
    @api.expect(group_put)
    @api.response(200, "Success")
    @api.response(404, "Could not find group")
    def put(self, id):
        group = models.Group.query.filter(models.Group.id == id).one_or_none()
        if group is None:
            abort(404)

        args = self.request_parser.parse_args()

        if args['groupname'] is not None:
            group.groupname = args['groupname']

        if args['name'] is not None:
            group.name = args['name']

        db.session.commit()
        db.session.refresh(group)

        return group
    
    @http_auth_required
    @permissions_required('group_delete')
    @api.response(200, "Success")
    @api.response(404, "Could not find group")
    def delete(self, id):
        group = models.Group.query.filter(models.Group.id == id).one_or_none()

        if group is None:
            abort(404)

        db.session.delete(group)
        db.session.commit()


@api.route('/groups/<id>/users', endpoint='groupusers')
class GroupUsersAPI(Resource):
    @http_auth_required
    @permissions_accepted('group_read', 'group_read_all')
    @api.marshal_with(user_list_get)
    @api.response(200, "Success")
    @api.response(403, "You are not authorized to get this information")
    @api.response(404, "Could not find group")
    def get(self, id):
        group = models.Group.query.filter(models.Group.id == id).one_or_none()

        if group is None:
            abort(404)

        if not has_permission_any('group_read_all'):
            if group not in current_user.groups:
                abort(403)

        return group


