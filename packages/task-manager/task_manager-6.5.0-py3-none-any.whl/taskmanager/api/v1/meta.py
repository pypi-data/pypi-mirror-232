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
from flask_restx import Resource, fields, reqparse
from flask_security import http_auth_required, permissions_accepted

from .base import api
from ... import models
from ...util.helpers import has_permission_any, get_object_from_arg

db = models.db

meta_history_fields = api.model('MetaHistory',{
    'id': fields.Integer,
    'timestamp': fields.DateTime,
    'value': fields.String,
})

meta_fields = api.model('Meta', {
    'id': fields.Integer,
    'label': fields.String,
    'value': fields.String,
    'history': fields.List(fields.Nested(meta_history_fields))
})

meta_list = api.model('MetaList', {
    'meta': fields.List(fields.Nested(meta_fields)),
})

meta_put = api.model('MetaPut', {
    'label': fields.String,
    'value': fields.String
})

@api.route('/meta', endpoint='meta')
class MetaListAPI(Resource):
    post_request_parser = reqparse.RequestParser()
    post_request_parser.add_argument('label', type=str, required=True, location='json')
    post_request_parser.add_argument('value', type=str, required=True, location='json')
    
    @http_auth_required
    @permissions_accepted('meta_read_all')
    @api.marshal_with(meta_list)
    @api.response(200, "Success")
    @api.response(403, "You are not authorized to get this information")
    def get(self):
        meta = models.Meta.query.all()
        
        if not has_permission_any('meta_read_all'):
            abort(403)

        return {"meta": meta}

    @http_auth_required
    @permissions_accepted('meta_add')
    @api.marshal_with(meta_fields)
    @api.expect(meta_put)
    @api.response(201, "Added new Meta entry")
    @api.response(403, "You are not authorized to do this operation")
    def post(self):  
        args = self.post_request_parser.parse_args()

        meta = models.Meta(label=args['label'], value=args['value'])
        
        db.session.add(meta)
        db.session.commit()
        db.session.refresh(meta)

        return meta, 201


@api.route('/meta/<id>', endpoint="meta_id")
class MetaAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('value', type=str, required=True, location='json')
    
    @http_auth_required
    @permissions_accepted('meta_read_all')
    @api.marshal_with(meta_fields)
    @api.response(200, "Success")
    @api.response(403, "You are not authorized to get this information")
    def get(self, id):
        meta = get_object_from_arg(id, models.Meta, models.Meta.label)

        if not has_permission_any('meta_read_all'):
            abort(403)

        if meta is None:
            abort(404)

        return meta

    @http_auth_required
    @permissions_accepted('meta_update')
    @api.marshal_with(meta_fields)
    @api.expect(meta_put)
    @api.response(200, "Success")
    @api.response(404, "Could not find Meta entry")
    def put(self, id):
        meta = get_object_from_arg(id, models.Meta, models.Meta.label)
        
        if meta is None:
            abort(404)

        args = self.request_parser.parse_args()

        meta.value = args['value']
        
        db.session.commit()
        db.session.refresh(meta)

        return meta
