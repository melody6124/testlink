# -*- coding:utf-8 -*-
import datetime
import os

import requests
import testlink

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = '7ccbcfc2d1c580277d7b5ce1038c9ee6'

tlc = testlink.TestlinkAPIClient(url, key)
test_project_name = os.getenv("PROJECT_TESTLINK", "ACP-master")
testproject_prefix = tlc.getTestProjectByName(test_project_name)["prefix"]
testsuite_id = tlc.getTestSuite("容器平台", testproject_prefix)[0]["id"]
subsuites = tlc.getTestSuitesForTestSuite(testsuiteid=testsuite_id)
wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
review_api_cases = []
review_ui_cases = []
for subsuite in subsuites.values():
    subsuite_id = subsuite["id"]
    cases = tlc.getTestCasesForTestSuite(testsuiteid=subsuite_id, deep=True, details='full')
    for case in cases:
        id = case["external_id"]
        type = case['execution_type']
        importance = case['importance']
        keyword = tlc.getTestCaseKeywords(testcaseexternalid=id)
        if keyword[id] != '':
            keywords = list(keyword[id].values())
            if 'api_no_automation' in keywords:
                review_api_cases.append(id)
            if 'ui_no_automation' in keywords:
                review_ui_cases.append(id)
print('当前检查的数据')
print(review_api_cases)
print(len(review_api_cases))
print('当前检查的数据')
print(review_ui_cases)
print(len(review_ui_cases))
today = datetime.date.today()
curren_dir = os.getcwd()
# 获取上一次的api数据
files = os.listdir("{}/api_no_automation".format(curren_dir))
api_file_name = "{}/api_no_automation/{}".format(curren_dir, files[-1])
file = open(api_file_name, 'r+', encoding='utf-8')
last_api_cases = file.read()
print('上次检查的数据 {}'.format(api_file_name))
print(last_api_cases)
file.close()
# 获取上一次的ui数据
files = os.listdir("{}/ui_no_automation".format(curren_dir))
ui_file_name = "{}/ui_no_automation/{}".format(curren_dir, files[-1])
file = open(ui_file_name, 'r+', encoding='utf-8')
last_ui_cases = file.read()
print('上次检查的数据 {}'.format(ui_file_name))
print(last_ui_cases)
file.close()

# 比较 api输出结果
review_api = ''
for case in review_api_cases:
    if case not in last_api_cases:
        detail = tlc.getTestCase(testcaseexternalid=case)
        review_api = review_api + "{}:{}\n".format(case, detail[0]['name'])
print(review_api)

if review_api != '':
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"<font color=\"warning\">新增api_no_automation的用例 需要评审</font> \n {review_api}"
        }
    }
    requests.post(wechat_webhook, json=msg)
# 比较 ui输出结果
review_ui = ''
for case in review_ui_cases:
    if case not in last_ui_cases:
        detail = tlc.getTestCase(testcaseexternalid=case)
        review_ui = review_ui + "{}:{}\n".format(case, detail[0]['name'])
print(review_ui)

if review_ui != '':
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"<font color=\"warning\">新增ui_no_automation的用例 需要评审 </font> \n {review_ui}"
        }
    }
    requests.post(wechat_webhook, json=msg)

# 当天的写入文件
api_file_name = "{}/api_no_automation/{}.txt".format(curren_dir, str(today))
file = open(api_file_name, 'w+', encoding='utf-8')
file.write(str(review_api_cases))
file.close()
ui_file_name = "{}/ui_no_automation/{}.txt".format(curren_dir, str(today))
file = open(ui_file_name, 'w+', encoding='utf-8')
file.write(str(review_ui_cases))
file.close()
