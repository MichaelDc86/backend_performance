#   Copyright 2021 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

""" Module """

import flask  # pylint: disable=E0401
import jinja2  # pylint: disable=E0401

from flask import request, render_template

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401

from ..shared.utils.api_utils import add_resource_to_api

from .init_db import init_db


class Module(module.ModuleModel):
    """ Task module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context

    def init(self):
        """ Init module """
        log.info("Initializing module Backend_performance")
        init_db()
        from .api.tests import TestsApi
        add_resource_to_api(self.context.api, TestsApi, "/backend/<int:project_id>")
        from .api.test import TestApiBackend
        add_resource_to_api(self.context.api, TestApiBackend, "/tests/<int:project_id>/backend/<string:test_id>")
        from .api.thresholds import BackendThresholdsAPI
        add_resource_to_api(self.context.api, BackendThresholdsAPI, "/thresholds/<int:project_id>/backend")
        from .api.baseline import BaselineAPI
        add_resource_to_api(self.context.api, BaselineAPI, "/baseline/<int:project_id>")
        from .api.reports import ReportAPI
        add_resource_to_api(self.context.api, ReportAPI, "/reports/<int:project_id>")
        from .api.charts import ReportChartsAPI
        add_resource_to_api(self.context.api, ReportChartsAPI, "/chart/<string:source>/<string:target>")

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing Backend_performance")
