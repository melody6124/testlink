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
# print(f"容器平台的二级目录ID:{parent_id}")
suite_assign = func_suite_assign

wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"


def list_test_case_smoke():
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
                keyword = tlc.getTestCaseKeywords(testcaseexternalid=id)
                if 'api' in str(keyword):
                    suite_tmp['api'].append(id)
                if importance == '3':
                    if 'smoke' in str(keyword):
                        suite_tmp['high_smoke'].append(id)
                else:
                    if 'smoke' in str(keyword):
                        suite_tmp['error_smoke'].append(id)
                suite_tmp['error_size'] = len(suite_tmp['error_smoke'])
            assign['error_total'] = assign['error_total'] + suite_tmp['error_size']
    return suite_assign


def send_error_smoke(result):
    vteam_error_total = 0
    for ret in result:
        vteam_error_total = vteam_error_total + ret['error_total']
    if vteam_error_total != 0:
        content = f"<font color=\"warning\">testlink还有{vteam_error_total}个用例keyword包含smoke,但级别不是High,请尽快调整Importance或者Keyword!!! </font>\n" \
                  f"<font color=\"info\">testlink可以搜索 Keyword=smoke Importance=Medium or Low </font>\n\n"
        for ret in result:
            if ret['error_total'] != 0:
                suites = []
                for suite in ret['suites']:
                    if suite['error_size'] != 0:
                        suites.append(suite['suitename'])
                content = content + "@{} {} 个用例 测试集{} \n".format(ret['user'], ret['error_total'], suites)
    else:
        content = "恭喜恭喜，testlink所有用例的smoke和importance对应正常"
    print(content)
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        }
    }
    ret = requests.post(wechat_webhook, json=msg)
    print(ret.text)


def send_high_smoke(result):
    content = "<font color=\"warning\">testlink还有功能模块High用例中没有smoke，请尽快调整Keyword!!! </font>\n\n"
    contents = ""
    for ret in result:
        suites = []
        for suite in ret['suites']:
            if len(suite['high_smoke']) == 0 and suite['suitename'] not in \
                    ['业务视图-计算组件>通用-容器组表单', '业务视图-计算组件>通用-详情页组件', '业务视图-计算组件>通用-局部更新', '业务视图-计算组件>通用-debug', '业务视图-计算组件>通用-镜像选择组件',
                     '业务视图-计算组件>通用-取消-阻断性提示', '业务视图-计算组件>asm-acp融合', '功能开关', '平台管理-ovn集群互通管理']:
                suites.append(suite['suitename'])
        if suites:
            contents = contents + "@{} 测试集 {}\n".format(ret['user'], suites)
    if contents != "":
        content = content + contents
    else:
        content = "恭喜恭喜，每个功能模块High的用例都有smoke"
    print(content)
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        }
    }
    ret = requests.post(wechat_webhook, json=msg)
    print(ret.text)


def send_api(result):
    content = "<font color=\"warning\">testlink还有功能模块用例中没有api，请尽快调整Keyword!!! </font>\n\n"
    contents = ""
    for ret in result:
        suites = []
        for suite in ret['suites']:
            if len(suite['api']) == 0 and suite['suitename'] not in \
                    ['业务视图-计算组件>通用-镜像选择组件', '业务视图-计算组件>通用-取消-阻断性提示', '业务视图-计算组件>asm-acp融合']:
                suites.append(suite['suitename'])
        if suites:
            contents = contents + "@{} 测试集 {}\n".format(ret['user'], suites)
    if contents != "":
        content = content + contents
    else:
        content = "恭喜恭喜，每个功能模块用例都有api"
    print(content)
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        }
    }
    ret = requests.post(wechat_webhook, json=msg)
    print(ret.text)


if __name__ == "__main__":
    result = list_test_case_smoke()
    print(result)
    send_high_smoke(result)
    send_error_smoke(result)
    send_api(result)
