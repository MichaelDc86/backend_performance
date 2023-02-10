from functools import partial

from flask import request
from flask_restful import Resource

from pylon.core.tools import log

from ...models.reports import Report
from ...connectors.minio_connector import MinioConnector
from ...connectors.influx_connector import InfluxConnector
from ...connectors.loki_connector import LokiConnector
from ...utils.charts_utils import requests_summary, requests_hits, avg_responses, summary_table, \
    get_data_for_analytics, get_issues, engine_health


class API(Resource):
    url_params = [
        '<string:source>/<string:target>',
    ]
    
    statuses = ('finished', 'error', 'failed', 'success')

    mapping = {
        "requests": {
            "summary": requests_summary,
            "hits": requests_hits,
            "average": avg_responses,
            "table": summary_table,
            "data": get_data_for_analytics
        },
        "errors": {
            "table": get_issues
        },
        "engine_health": {
            "cpu": partial(engine_health, part='cpu'),
            "memory": partial(engine_health, part='memory'),
            "load": partial(engine_health, part='load'),
            "all": engine_health,
        }
    }

    def __init__(self, module):
        self.module = module


    def get(self, source: str, target: str):
        connector = None
        args = request.args.to_dict(flat=True)
        # args['source'] = 'minio'
        for i in request.args.keys():
            if i.endswith('[]'):
                args[i] = request.args.getlist(i)
        connector = self._get_connector(args, source)
        return self.mapping[source][target](args, connector)
    
    
    def _get_connector(self, args, source):
        test_status = Report.query.with_entities(Report.test_status).filter(
            Report.build_id == args['build_id']
            ).first()[0]['status'].lower()
        if test_status in self.statuses:
            log.info('Using MinioConnector')
            return MinioConnector(**args)
        else:
            if source == "errors":
                log.info('Using LokiConnector')
                return LokiConnector(**args)            
            elif source == "engine_health":
                project_id = Report.query.with_entities(Report.project_id).filter(
                    Report.build_id == args['build_id']
                    ).first()[0]
                args['db_name'] = f'telegraf_{project_id}'
                log.info(f'Using InfluxConnector with DB telegraf_{project_id}')
                return InfluxConnector(**args)
            else:
                log.info('Using InfluxConnector')
                return InfluxConnector(**args)                
