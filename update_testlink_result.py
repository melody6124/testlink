# coding=utf-8
import re

import testlink
from bs4 import BeautifulSoup

# from common import settings

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = '7ccbcfc2d1c580277d7b5ce1038c9ee6'
testproject_name = "ACP-3.6.x"  # settings.TESTPROJECT_NAME
testplan_name = "acp3.6.4发版第一轮测试 - API自动化回归"  # settings.TESTPLAN_NAME
testbuild_name = "acp3.6.4发版第一轮测试 - API自动化回归"  # settings.TESTBUILD_NAME
report_path = "3.6.4发版测试第二轮ovn集群HIgh结果.html"

tlc = testlink.TestlinkAPIClient(url, key)

def update_result():
    testproject_prefix = tlc.getTestProjectByName(testproject_name)['prefix']
    testplan_id = tlc.getTestPlanByName(testproject_name, testplan_name)[0]['id']
    testcases = tlc.getTestCasesForTestPlan(testplanid=testplan_id)
    external_ids = []
    for key in testcases:
        for case in testcases[key]:
            external_ids.append(case['external_id'])
    print("start update testlink result")
    with open(report_path, "r") as fp:
        report = BeautifulSoup(fp, "html.parser")
        tbodys = report.select("tbody")
        for tbody in tbodys:
            tds = tbody.select("td")
            if len(re.findall('[0-9]{4,6}', tds[1].text)) > 0:
                for id in re.findall('[0-9]{4,6}', tds[1].text):
                    if id in external_ids:
                        case_id = "{}-{}".format(testproject_prefix, id)
                        print("开始更新 {}".format(case_id))
                        if tds[0].text == "Skipped":
                            tlc.reportTCResult(testcaseexternalid=case_id, testplanid=testplan_id,
                                               buildname=testbuild_name,
                                               status='b')
                        elif tds[0].text == "Passed" and tds[2].text != "0.00":
                            tlc.reportTCResult(testcaseexternalid=case_id, testplanid=testplan_id,
                                               buildname=testbuild_name,
                                               status='p')
                        elif tds[0].text == "Failed" or tds[0].text == "Error":
                            tlc.reportTCResult(testcaseexternalid=case_id, testplanid=testplan_id,
                                               buildname=testbuild_name,
                                               status='f')
                    else:
                        print("不在测试计划内，忽略更新 {}-{}".format(testproject_prefix, id))


if __name__ == "__main__":
    update_result()
