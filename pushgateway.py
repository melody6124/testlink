# -*- coding:utf-8 -*-

import requests


def pushgateway(metric, instance, value):
    push_url = f'http://192.168.176.150:30901/metrics/job/acp_qa_testlink'
    headers = {
        'Content-Type': 'multipart/form-data'
    }
    label = "{instance=\"" + instance + "\",metric=\"" + metric + "\"}"
    data = f"{metric}{label} {value}"
    push_data = f"""
    {data}
    """
    print(push_data)
    ret = requests.post(push_url, data=push_data.encode('utf-8'), headers=headers)
    print(ret)


if __name__ == '__main__':
    pushgateway("api_coverage", "施源", 4)
