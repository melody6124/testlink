# -*- coding:utf-8 -*-
import os

import requests
import testlink

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = 'ce5899e587724a8945c732ed3ff37ff7'

tlc = testlink.TestlinkAPIClient(url, key)
test_project_name = os.getenv("PROJECT_TESTLINK", "ACP-master")
test_project_prefix = tlc.getTestProjectByName(test_project_name)['prefix']
testproject_id = tlc.getProjectIDByName(test_project_name)

suite_assign = [
    {"user": "周瑜", "total": 0, "suitename": "场景测试", "detail": []},
    {"user": "周瑜", "total": 0, "suitename": "common", "detail": []},
    {"user": "史京南", "total": 0, "suitename": "容器平台", "detail": []},
    {"user": "刘伟", "total": 0, "suitename": "ASM", "detail": []},
    {"user": "杨焕", "total": 0, "suitename": "DevOps", "detail": []},
    {"user": "韩后超", "total": 0, "suitename": "基础架构", "detail": []},
    {"user": "陈金虎", "total": 0, "suitename": "中间件", "detail": []},
    {"user": "周瑜", "total": 0, "suitename": "MLops", "detail": []},
]


def list_test_case_not_reviewed():
    for assign in suite_assign:
        parent_id = tlc.getTestSuite(assign["suitename"], test_project_prefix)[0]["id"]
        test_suites = tlc.getTestSuitesForTestSuite(parent_id)
        for test_suite in list(test_suites.values()):
            print(test_suite)
            testsuite_name = test_suite['name']
            testsuite_id = test_suite['id']
            cases = tlc.getTestCasesForTestSuite(testsuiteid=testsuite_id, deep=True, details='full')
            size = 0
            for case in cases:
                status = case["status"]
                if status != '7':
                    size = size + 1
            if size != 0:
                assign['detail'].append(f"{testsuite_name} {size}")
                assign['total'] = assign['total'] + size
    return suite_assign


def send_content(result):
    content = ""
    for ret in result:
        if ret['total'] != 0:
            content = content + "@{} {} {} 个用例 测试集{} \n\n".format(ret['user'], ret['suitename'], ret['total'], ret['detail'])
    if content != "":
        content = f"testlink还有用例Status不是Final,请尽快用例评审!!!\n" \
                  f"测试用例评审流程 https://confluence.alauda.cn/pages/releaseview.action?pageId=75094349 \n\n{content}"
        print(content)
        wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=7b61450b-5a61-4bb1-9539-8e993218d5f7"
        msg = {
            "msgtype": "text",
            "text": {
                "content": content,
            }
        }
        ret = requests.post(wechat_webhook, json=msg)
        print(ret.status_code)
        print(ret.text)


if __name__ == "__main__":
    result = list_test_case_not_reviewed()
    send_content(result)
