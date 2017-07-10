#!/usr/bin/env python

from __future__ import print_function, unicode_literals

from sys import argv
from io import BytesIO

from json import loads, dumps

# Satisfy grafanalib
class machinery:
    SourceFileLoader = None
import sys
sys.modules['importlib.machinery'] = machinery

import grafanalib.core as G
from grafanalib._gen import write_dashboard

from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react

from txkube import network_kubernetes_from_context


def dashboard():
    return G.Dashboard(
        title="S4",
        rows=[
            G.Row(panels=[
                G.SingleStat(
                    title='Current Customer Deployments',
                    dataSource='prometheus',
                    valueName='current',
                    sparkline=G.SparkLine(show=True),
                    targets=[
                        G.Target(
                            expr='s4_deployment_gauge',
                        ),
                    ],
                ),
                G.SingleStat(
                    title='Signups',
                    dataSource='prometheus',
                    valueName='current',
                    sparkline=G.SparkLine(show=True),
                    targets=[
                        G.Target(
                            expr='s4_signup_counter',
                        ),
                    ],
                ),
                G.SingleStat(
                    title='Unhandled Errors',
                    dataSource='prometheus',
                    valueName='current',
                    sparkline=G.SparkLine(show=True),
                    targets=[
                        G.Target(
                            expr='s4_unhandled_error_counter',
                        ),
                    ],
                ),
            ]),
        ],
    ).auto_panel_ids()




def dashboard_to_json_bytes(dashboard):
    io = BytesIO()
    write_dashboard(dashboard, io)
    dashboard_json_bytes = io.getvalue()
    return dashboard_json_bytes



def configmap(model, dashboard):
    return model.v1.ConfigMap(
        metadata={
            "name": "grafana-dashboards",
            "labels": {
                "provider": "LeastAuthority",
                "component": "Monitoring",
                "service": "grafana",
            },
        },
        data={
            "prometheus-datasource.json": dumps({
                'access': 'proxy',
                'basicAuth': False,
                'name': 'prometheus',
                'type': 'prometheus',
                'url': 'http://prometheus/',
                'orgId': 1,
            }).decode("ascii"),
            "s4-dashboard.json": dumps({
                "dashboard": loads(dashboard_to_json_bytes(dashboard)),
                "overwrite": True,
            }).decode("ascii"),
        },
    )


@inlineCallbacks
def main(reactor, context):
    kubernetes = network_kubernetes_from_context(reactor, context)
    client = yield kubernetes.client()
    model = client.model
    cfg = model.iobject_to_raw(configmap(model, dashboard()))
    print(dumps(cfg))


if __name__ == '__main__':
    react(main, argv[1:])