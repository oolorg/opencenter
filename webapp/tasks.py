#!/usr/bin/env python

import json
from time import time

from flask import Blueprint, Flask, Response, request
from flask import session, jsonify, url_for, current_app

from db import api as api
from db import exceptions as exc
from db.database import db_session
from webapp.errors import (
    http_bad_request,
    http_conflict,
    http_not_found,
    http_not_implemented)

from filters import AstBuilder, FilterTokenizer

tasks = Blueprint('tasks', __name__)


@tasks.route('/', methods=['GET', 'POST'])
def list_tasks():
    if request.method == 'POST':
        fields = api.task_get_columns()
        data = dict((field, request.json[field] if (field in request.json)
                     else None) for field in fields)
        try:
            task = api.task_create(data)
            href = request.base_url + str(task['id'])
            msg = {'status': 201,
                   'message': 'Tasl Created',
                   'task': task,
                   'ref': href}
            resp = jsonify(msg)
            resp.status_code = 201
            resp.headers['Location'] = href
        except exc.CreateError, e:
            return http_bad_request(e.message)
    else:
        tasks = api.tasks_get_all()
        resp = jsonify({'tasks': tasks})
    return resp


@tasks.route('/filter', methods=['POST'])
def filter_tasks():
    builder = AstBuilder(FilterTokenizer(),
                         'tasks: %s' % request.json['filter'])
    return jsonify({'tasks': builder.eval()})


@tasks.route('/<task_id>', methods=['GET', 'PUT'])
def task_by_id(task_id):
    if request.method == 'PUT':
        fields = api.task_get_columns()
        data = dict((field, request.json[field]) for field in fields
                    if field in request.json)
        task = api.task_update_by_id(task_id, data)
        resp = jsonify({'task': task})
        return resp
    else:
        task = api.task_get_by_id(task_id)
        if not task:
            return http_not_found()
        else:
            resp = jsonify({'task': task})
            return resp
