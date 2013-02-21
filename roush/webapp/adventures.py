#!/usr/bin/env python
#
# Copyright 2012, Rackspace US, Inc.
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
#

import flask

from roush.db.api import api_from_models
from roush.db import exceptions
from roush.webapp import generic
# from roush.webapp import solver
# from roush.webapp import utility


object_type = 'adventures'
bp = flask.Blueprint(object_type, __name__)


@bp.route('/', methods=['GET', 'POST'])
def list():
    return generic.list(object_type)


@bp.route('/<object_id>', methods=['GET', 'PUT', 'DELETE'])
def by_id(object_id):
    return generic.object_by_id(object_type, object_id)


@bp.route('/<adventure_id>/execute', methods=['POST'])
def execute_adventure(adventure_id):
    data = flask.request.json

    if not 'node' in data:
        return generic.http_badrequest(msg='node not specified')

    api = api_from_models()
    try:
        adventure = api._model_get_by_id('adventures', int(adventure_id))
    except exceptions.IdNotFound:
        message = 'Not Found: Adventure %s' % adventure_id
        return generic.http_notfound(msg=message)

    try:
        return generic.http_solver_request(data['node'], [],
                                           api=api, plan=adventure['dsl'])
    except exceptions.IdNotFound:
        #Can IdNotFound be raised for any other reason?
        return generic.http_notfound(msg='Not Found: Node %s' % data['node'])
