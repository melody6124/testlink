# -*- coding:utf-8 -*-
import json
import re
import testlink

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = 'ce5899e587724a8945c732ed3ff37ff7'
testplan_name = "ACP3.13发版测试-第一轮手动测试"
build_name = "r1"
test_project_name = "ACP-3.13.x"
report = "report_002.json"

tlc = testlink.TestlinkAPIClient(url, key)


def update_case_status(testplan_id, case_id, status, buildid):
    try:
        id = tlc.getTestCase(testcaseexternalid=case_id)[0]['testcase_id']
        # 当testlink上case状态是pass就不再更新结果了
        if tlc.getTestCasesForTestPlan(testplanid=testplan_id, buildid=int(buildid), testcaseid=int(id))[id][0]["exec_status"] != "p":
            tlc.reportTCResult(testcaseexternalid=case_id, testplanid=testplan_id, buildname=build_name, status=status)
        return True
    except Exception as e:
        print("更新testlink失败:{}".format(e))
        return False


def get_testplan_id():
    testplan = tlc.getTestPlanByName(test_project_name, testplan_name)
    testplan_id = testplan[0]["id"]
    return testplan_id


def report_test_result():
    test_project_prefix = tlc.getTestProjectByName(test_project_name)['prefix']
    testplan_id = get_testplan_id()
    buildid = ""
    builds_info = tlc.getBuildsForTestPlan(testplan_id)
    for build_info in builds_info:
        if build_info["name"] == build_name:
            buildid = build_info["id"]
    with open(report, 'r', encoding='utf-8') as f:
        json_content = json.load(f)
        for result in json_content['results']:
            if "cypress/e2e/acp" in result['fullFile']:
                # print(result['fullFile'])
                for suite in result['suites']:
                    for test in suite['tests']:
                        case_name = test['fullTitle']
                        for id in (re.findall('[0-9]{4,6}', case_name)):
                            case_id = test_project_prefix + "-" + id
                            if test['pass']:
                                update_case_status(testplan_id, case_id, "p", buildid)
                            if test['fail']:
                                print(case_name)
                                update_case_status(testplan_id, case_id, "f", buildid)


if __name__ == "__main__":
    report_test_result()
