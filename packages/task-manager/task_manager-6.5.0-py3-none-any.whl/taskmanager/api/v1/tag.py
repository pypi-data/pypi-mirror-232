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
from flask_security import http_auth_required, permissions_accepted

from .base import api
from ... import models, db
from ...fields import ObjectUrl, SubUrl


tag_summary = api.model('TagSummary',
          {
              'uri': ObjectUrl('api_v1.tag', attribute='id'),
              'name': fields.String,
          }
)


tag_list_get = api.model("TagListGet", {
    'tags': fields.List(fields.Nested(tag_summary))
})

tag_get = api.model("TagGet",
    {
        'name': fields.String,
        'uri': fields.Url('api_v1.tag'),
        'tasks': SubUrl('api_v1.tag', 'tasks', attribute='id')
    }
)


tag_put = api.model("TagPut", {
    'name': fields.String,
})


@api.route('/tags', endpoint='tags')
class TagListAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('name', type=str, required=True, location='json')

    @http_auth_required
    @api.marshal_with(tag_list_get)
    def get(self):
        tags = models.Tag.query.all()
        return {'tags': tags}

    @http_auth_required
    @permissions_accepted('tag_add')
    @api.marshal_with(tag_get)
    @api.expect(tag_put)
    @api.response(201, "Created tag")
    def post(self):
        tag = models.Tag(**self.request_parser.parse_args())
        db.session.add(tag)
        db.session.commit()
        db.session.refresh(tag)
        return tag, 201


@api.route('/tags/<int:id>', endpoint='tag')
class TagAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('name', type=str, required=False, location='json')

    @http_auth_required
    @api.marshal_with(tag_get)
    @api.response(200, "Success")
    @api.response(404, "Could not find tag")
    def get(self, id):
        tag = models.Tag.query.filter(models.Tag.id == id).one_or_none()
        if tag is None:
            abort(404)
        return tag

    @http_auth_required
    @permissions_accepted('tag_update')
    @api.marshal_with(tag_get)
    @api.expect(tag_put)
    @api.response(200, "Success")
    @api.response(404, "Could not find tag")
    def put(self, id):
        tag = models.Tag.query.filter(models.Tag.id == id).one_or_none()
        if tag is None:
            abort(404)

        args = self.request_parser.parse_args()

        if args['name'] is not None:
            tag.project = args['name']

        db.session.commit()
        db.session.refresh(tag)
        return tag

    @http_auth_required
    @permissions_accepted('tag_delete')
    @api.response(200, "Success")
    @api.response(404, "Could not find tag")
    def delete(self, id):
        tag = models.Tag.query.filter(models.Tag.id == id).one_or_none()
        if tag is None:
            abort(404)

        db.session.delete(tag)
        db.session.commit()
