# -*- coding:utf-8 -*-
import os

import requests
import testlink

from division import func_suite_assign

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = 'ce5899e587724a8945c732ed3ff37ff7'

tlc = testlink.TestlinkAPIClient(url, key)
test_project_name = os.getenv("PROJECT_TESTLINK", "ACP-master")
test_project_prefix = tlc.getTestProjectByName(test_project_name)['prefix']
testproject_id = tlc.getProjectIDByName(test_project_name)
parent_suite = "容器平台"
parent_id = tlc.getTestSuite(parent_suite, test_project_prefix)[0]["id"]
suite_assign = func_suite_assign


def list_test_case_importance():
    result = [{'user': '史京南', 'no_high_suites': [], 'no_low_suites': []},
              {'user': '赵晓峰', 'no_high_suites': [], 'no_low_suites': []},
              {'user': '郑虎林', 'no_high_suites': [], 'no_low_suites': []},
              {'user': '施源', 'no_high_suites': [], 'no_low_suites': []},
              {'user': '王珂', 'no_high_suites': [], 'no_low_suites': []},
              {'user': '刘明宇', 'no_high_suites': [], 'no_low_suites': []}, ]
    for assign in suite_assign:
        ind = suite_assign.index(assign)
        for suite_tmp in assign['suites']:
            suites = suite_tmp["suitename"].split(">")
            global testsuite_id
            testsuite_id = parent_id
            for index, suite in enumerate(suites):
                if index <= len(suites) - 1:
                    test_suites = tlc.getTestSuitesForTestSuite(testsuite_id)
                    for test_suite in list(test_suites.values()):
                        if suite == test_suite["name"]:
                            testsuite_id = test_suite["id"]
                            break
            if testsuite_id == parent_id:
                print(f"当前路径不存在{suite}")
                continue
            cases = tlc.getTestCasesForTestSuite(testsuiteid=testsuite_id, deep=True, details='full')
            for case in cases:
                id = case["external_id"]
                importance = case["importance"]
                if importance == '1':
                    suite_tmp['low_detail'].append(id)
                elif importance == '3':
                    suite_tmp['high_detail'].append(id)
            len(suite_tmp['low_detail'])
            if len(suite_tmp['low_detail']) == 0:
                result[ind]['no_low_suites'].append(suite_tmp['suitename'])
            if len(suite_tmp['high_detail']) == 0:
                result[ind]['no_high_suites'].append(suite_tmp['suitename'])
    return result


def send_content(result):
    content = "<font color=\"warning\">testlink还有功能模块没有High或者Low的用例，请尽快调整Importance!!!</font> \n\n"
    contents = ""
    for ret in result:
        if '业务视图-计算组件>asm-acp融合' in ret['no_high_suites']:
            ret['no_high_suites'].remove('业务视图-计算组件>asm-acp融合')
        if len(ret['no_high_suites']) != 0:
            contents = contents + "@{} 没有High 的测试集 {}\n".format(ret['user'], ret['no_high_suites'])
        if len(ret['no_low_suites']) != 0:
            contents = contents + "@{} 没有Low  的测试集 {}\n".format(ret['user'], ret['no_low_suites'])
    if contents != "":
        content = content + contents
    else:
        content = "恭喜恭喜，每个功能模块的优先级都比较合理"
    print(content)
    wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        }
    }
    requests.post(wechat_webhook, json=msg)


if __name__ == "__main__":
    result = list_test_case_importance()
    print(result)
    send_content(result)
