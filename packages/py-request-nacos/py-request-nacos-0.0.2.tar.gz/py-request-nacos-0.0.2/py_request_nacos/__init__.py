import requests
import json
import numpy as np


def request_nacos(nacos_url='http://82.157.147.8:8848/nacos', service_name='encourager'):
    result = requests.get(nacos_url + '/v1/ns/instance/list?serviceName=' + service_name).text
    result_json = json.loads(result)
    hosts = result_json['hosts']
    return hosts[np.random.randint(0, len(hosts))]['ip'], hosts[np.random.randint(0, len(hosts))]['port']