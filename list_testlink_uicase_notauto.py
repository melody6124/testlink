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
suite_assign = ui_suite_assign


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
                    if execution_type_ui != 'Automated':
                        keyword = tlc.getTestCaseKeywords(testcaseexternalid=id)
                        if 'smoke' in str(keyword) and 'ui_no_automation' not in str(keyword):
                            suite_tmp['detail'].append(id)
            suite_tmp['size'] = len(suite_tmp['detail'])
            assign['total'] = assign['total'] + suite_tmp['size']
    return suite_assign


def send_content(result):
    vteam_total = 0
    for ret in result:
        vteam_total = vteam_total + ret['total']
    if vteam_total != 0:
        content = f"<font color=\"warning\">testlink还有{vteam_total}个用例 优先级是High且smoke但没有加UI自动化,请检查!!!如果不能写自动化，请找赵晓峰确认后加上keyword:ui_no_automation </font>\n" \
                  f"<font color=\"info\">testlink可以搜索 Keyword包含smoke 不包含ui_no_automation;Importance=High;execution_type_ui=Manual </font>\n\n"
        for ret in result:
            if ret['total'] != 0:
                suites = []
                for suite in ret['suites']:
                    if suite['size'] != 0:
                        suites.append(suite['suitename'])
                content = content + "@{} {} 个用例 测试集{} \n".format(ret['user'], ret['total'], suites)
    else:
        content = "恭喜恭喜，testlink High smoke的用例都加完UI自动化啦"
    print(content)
    if content != "":
        wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=7b61450b-5a61-4bb1-9539-8e993218d5f7"
        msg = {
            "msgtype": "markdown",
            "markdown": {
                "content": content,
            }
        }
        ret = requests.post(wechat_webhook, json=msg)
        print(ret.status_code)
        print(ret.text)


if __name__ == "__main__":
    result = list_test_case_not_automated()
    send_content(result)
