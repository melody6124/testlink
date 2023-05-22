# -*- coding:utf-8 -*-
import os

import requests
import testlink

from division import api_suite_assign

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = 'e01c9b95bafdfa50d9cc7eedaa6ca082'
tlc = testlink.TestlinkAPIClient(url, key)
test_project_name = os.getenv("PROJECT_TESTLINK", "ACP-master")
test_project_prefix = tlc.getTestProjectByName(test_project_name)['prefix']
testproject_id = tlc.getProjectIDByName(test_project_name)
parent_suite = "容器平台"
parent_id = tlc.getTestSuite(parent_suite, test_project_prefix)[0]["id"]
# print(f"容器平台的二级目录ID:{parent_id}")
suite_assign = api_suite_assign.copy()
suite_assign.pop(0)


def list_test_case_not_automated():
    for assign in suite_assign:
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
                execution_type = case["execution_type"]
                # importance 3-high 2-medium 3-low
                # execution_type 1 Manual 2 Automated
                if importance in ['3', '2', '1']:
                    keyword = tlc.getTestCaseKeywords(testcaseexternalid=id)
                    if 'api' in str(keyword) and 'api_no_automation' not in str(keyword):
                        suite_tmp['size'] = suite_tmp['size'] + 1
                        if execution_type == '1':
                            suite_tmp['detail'].append(id)
    return suite_assign


def send(content):
    wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        }
    }
    ret = requests.post(wechat_webhook, json=msg)
    print(ret.text)


def send_content(result):
    for ret in result:
        ready = ""
        notready = ""
        total = 0
        no_total = 0
        for suite in ret['suites']:
            total = total + suite['size']
            if suite['size'] > 0:
                if len(suite['detail']) / suite['size'] > 0.2:
                    no_total = no_total + len(suite['detail'])
                    notready = notready + "{} {}/{} {} \n".format(suite['suitename'], len(suite['detail']), suite['size'],
                                                                  "%.0f%%" % ((suite['size'] - len(suite['detail'])) / suite['size'] * 100))
                else:
                    ready = ready + "{} {}/{} {}\n".format(suite['suitename'], len(suite['detail']), suite['size'],
                                                           "%.0f%%" % ((suite['size'] - len(suite['detail'])) / suite['size'] * 100))
        content = f"<font color=\"warning\">{ret['user']} {no_total}/{total}</font> \n"
        if notready != "":
            content = content + f"<font color=\"warning\">testlink还有功能模块 API自动化覆盖率没超过80%,请检查!!!如果不能写自动化，请找史京南确认后加上keyword:api_no_automation</font> \n" \
                                f"<font color=\"info\">testlink可以搜索 Keyword包含api 不包含api_no_automation;Execution Type=Manual</font> \n" \
                                f"<font color=\"info\">未达标的结果 模块 未覆盖数/总数 覆盖率 </font>\n"
            content = content + notready
        if ready != "":
            content = content + f"<font color=\"info\">以下模块 API自动化覆盖率都超过80%啦</font>\n\n"
            content = content + ready
        print(content)
        send(content)


if __name__ == "__main__":
    result = list_test_case_not_automated()
    print(result)
    send_content(result)
