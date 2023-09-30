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

from flask import abort, jsonify
from flask_restx import fields, Resource, reqparse
from flask_security import current_user, http_auth_required, permissions_accepted

from .base import api
from ... import models, db
from ...fields import ObjectUrl
from ...util.helpers import has_permission_any

def user_type(value):
    if value is None:
        return None
    elif isinstance(value, int):
        return value
    else:
        return str(value)


lock_get = api.model('LockGet', {
    'lock': ObjectUrl('api_v1.user', object_id='id'),
    'username': fields.String,
    'error': fields.String
})


lock_put = api.model('LockPut', {
    'lock': ObjectUrl('api_v1.user', object_id='id'),
})


@api.route('/tasks/<int:id>/lock', endpoint='lock')
class LockAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('lock', type=user_type, required=False, location='json')

    @http_auth_required
    @permissions_accepted('task_read', 'task_read_all')
    @api.marshal_with(lock_get)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find selected task')
    def get(self, id):
        query = models.Task.query.filter(models.Task.id == id)
        if not has_permission_any('task_read_all'):
            tasks_via_user_query = query.filter(models.Task.users.contains(current_user))
            tasks_via_group_query = query.filter(models.Task.users_via_group.contains(current_user))
            query = tasks_via_user_query.union(tasks_via_group_query)
        task = query.one_or_none()

        if task is None:
            abort(404)

        if task.lock is None:
            return jsonify({'lock': None, 'error': None})

        result = {
            "lock": task.lock,
            "username": task.lock.username if task.lock is not None else None,
            "error": None
        }
        return result

    @http_auth_required
    @permissions_accepted('task_read', 'task_update_lock_all', 'task_update_all')
    @api.marshal_with(lock_get)
    @api.response(200, 'Success')
    @api.response(403, 'You are not authorized to release the lock of another user')
    @api.response(404, 'Could not find selected task or user')
    def delete(self, id):
        query = models.Task.query.filter(models.Task.id == id)
        if not has_permission_any('task_update_lock_all', 'task_update_all'):
            tasks_via_user_query = query.filter(models.Task.users.contains(current_user))
            tasks_via_group_query = query.filter(models.Task.users_via_group.contains(current_user))
            query = tasks_via_user_query.union(tasks_via_group_query)
        task = query.one_or_none()

        if task is None:
            result = {"error": f'Could not find the specified task lock (task {id} does not exist)!',
                      "username": None,
                      "lock": None}
            return result, 404

        if task.lock is not None and task.lock != current_user and not has_permission_any('task_update_lock_all', 'task_update_all'):
            # If the task is locked and not by you and you are not authorized to update all locks, throw 403.
            result = {"error": 'You are not authorized to release the lock of a task, assigned to someone else!',
                        "username": None, "lock": None}
            return result, 403
        else:
            # You are authorized to release this lock.
            task.lock = None
            result = {"lock": None, "username": None, "error": None}
            db.session.commit()
            return result
    
    @http_auth_required
    @permissions_accepted('task_read', 'task_update_lock_all', 'task_update_all')
    @api.marshal_with(lock_get)
    @api.expect(lock_put)
    @api.response(200, 'Success')
    @api.response(403, 'You are not authorized to update the lock this task to someone else')
    @api.response(404, 'Could not find selected task or user')
    @api.response(409, 'Task already locked by other user')
    def put(self, id):
        query = models.Task.query.filter(models.Task.id == id)
        if not has_permission_any('task_update_lock_all', 'task_update_all'):
            tasks_via_user_query = query.filter(models.Task.users.contains(current_user))
            tasks_via_group_query = query.filter(models.Task.users_via_group.contains(current_user))
            query = tasks_via_user_query.union(tasks_via_group_query)
        task = query.one_or_none()

        if task is None:
            result = {"error": f'Could not find the specified task lock (task {id} does not exist)!',
                      "username": None,
                      "lock": None}
            return result, 404

        args = self.request_parser.parse_args()
        if args['lock']:
            # Lock is given, now try to set the lock
            lock = args['lock']
            if isinstance(lock, int):
                user = models.User.query.filter(models.User.id == lock).one_or_none()
            else:
                user = models.User.query.filter(models.User.username == lock).one_or_none()

            if user is None:
                result = {"lock": task.lock,
                          "username": task.lock.username if task.lock is not None else None,
                          "error": f'Could not find the specified user to update lock to (user {lock} does not exist)!'}
                return result, 404

            if task.lock is not None and task.lock != user:
                if has_permission_any('task_update_lock_all', 'task_update_all'):
                    # This user has the right permission to overwrite any lock, so proceed.
                    task.lock = user
                else:
                    # This user is not authorized to overwrite a lock from another user.
                    result = {"lock": task.lock,
                              "username": task.lock.username if task.lock is not None else None,
                              "error": 'Task already locked!'}
                    return result, 409

            if has_permission_any('task_update_lock_all', 'task_update_all'):
                # When a user has a task_update_lock_all and/or task_update_all permission, the lock
                # may be (over)written at all times to the specified user.
                task.lock = user
            else:
                # When a user does not have an *_all permission, the user may still lock a task of itself.
                if user == current_user:
                    # This is allowed! A user can lock its own to task itself.
                    task.lock = user
                else:
                    result = {"lock": task.lock,
                              "username": task.lock.username if task.lock is not None else None,
                              "error": 'You may not lock this task to another user'}
                    return result, 403

        else:
            # No lock is given in the arguments, try to lock this task to the requesting user.
            if task.lock is not None and task.lock != current_user:
                # A lock already has been set 
                result = {"lock": task.lock,
                          "username": task.lock.username if task.lock is not None else None,
                          "error": 'Task already locked!'}
                return result, 409
            else:
                task.lock = current_user

        # Commit all changes to the database 
        db.session.commit()
        db.session.refresh(task)

        result = {
            "lock": task.lock,
            "username": task.lock.username if task.lock is not None else None,
            "error": None
        }
        return result
