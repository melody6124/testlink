# -*- coding:utf-8 -*-
import os

import requests
import testlink

from division import ui_suite_assign

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = 'ce5899e587724a8945c732ed3ff37ff7'

tlc = testlink.TestlinkAPIClient(url, key)
test_project_name = os.getenv("PROJECT_TESTLINK", "ACP-master")
test_project_prefix = tlc.getTestProjectByName(test_project_name)['prefix']
testproject_id = tlc.getProjectIDByName(test_project_name)
parent_suite = "容器平台"
parent_id = tlc.getTestSuite(parent_suite, test_project_prefix)[0]["id"]
# print(f"容器平台的二级目录ID:{parent_id}")
suite_assign = ui_suite_assign.copy()
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
                if importance == '3':
                    version = int(case["version"])
                    execution_type_ui = tlc.getTestCaseCustomFieldDesignValue(testcaseexternalid=id, version=version, testprojectid=testproject_id,
                                                                              customfieldname="execution_type_ui")
                    if importance in ['3']:
                        keyword = tlc.getTestCaseKeywords(testcaseexternalid=id)
                        if 'ui_no_automation' not in str(keyword):
                            suite_tmp['size'] = suite_tmp['size'] + 1
                            if execution_type_ui == 'Automated':
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
    print(ret.status_code)
    print(ret.text)


def send_content(result):
    for ret in result:
        contents = ""
        total = 0
        no_total = 0
        for suite in ret['suites']:
            total = total + suite['size']
            no_total = no_total + (suite['size'] - len(suite['detail']))
            if suite['size'] != 0 and len(suite['detail']) / suite['size'] != 1:
                contents = contents + "{} {}/{} {} \n".format(suite['suitename'], suite['size'] - len(suite['detail']), suite['size'],
                                                              "%.0f%%" % (len(suite['detail']) / suite['size'] * 100))
        if contents != "":
            content = f"<font color=\"warning\">{ret['user']} {no_total}/{total}\n还有功能模块 High UI自动化覆盖率没超过100%,请检查!!!如果不能写自动化，请找赵晓峰确认后加上keyword:ui_no_automation </font>\n" \
                      f"<font color=\"info\">testlink可以搜索 Keyword不包含ui_no_automation;Importance=High;execution_type_ui=Manual </font>\n" \
                      f"<font color=\"info\">结果为 模块 未覆盖数/总数 覆盖率 </font>\n"
            content = content + contents
            print(content)
            send(content)


if __name__ == "__main__":
    result = list_test_case_not_automated()
    print(result)
    send_content(result)
