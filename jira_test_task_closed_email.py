# -*- coding: utf-8 -*-
import requests
import testlink
from jira import JIRA

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = '7ccbcfc2d1c580277d7b5ce1038c9ee6'

tlc = testlink.TestlinkAPIClient(url, key)
test_project_name = "ACP-master"
testproject_id = tlc.getProjectIDByName(test_project_name)
plans = tlc.getProjectTestPlans(testproject_id)

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = 'project = ACP AND (summary ~ 测试任务 or summary ~ 功能测试执行) AND issuetype in (Job, Task) AND resolution in (Done, "Pass Test") AND resolved >= -1d'
issues = jira.search_issues(jql)
closed = ""
no_testplan = ""
mentioned_list = []
no_testplan_mentioned_list = []

for i in issues:
    reporter = str(i.fields.assignee)
    mentioned_list.append(i.fields.assignee.name)
    closed = closed + '@{} http://jira.alauda.cn/browse/{} {} \n'.format(reporter, i.key, i.fields.summary)
    plan_name = ''
    for plan in plans:
        if i.key in plan['name']:
            plan_name = plan['name']
            break
    if plan_name == '':
        no_testplan = no_testplan + '@{} http://jira.alauda.cn/browse/{} {} \n'.format(reporter, i.key, i.fields.summary)
        no_testplan_mentioned_list.append(i.fields.assignee.name)

if closed != "":
    content = "过去一天关闭的测试任务，发功能测试结果的邮件了吗？\n" \
              "邮件模版参考 https://confluence.alauda.cn/pages/viewpage.action?pageId=86341102 \n\n{}".format(closed)
    print(content)
    wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": list(set(mentioned_list))
        }
    }
    requests.post(wechat_webhook, json=msg)

if no_testplan != "":
    content = "过去一天关闭的测试任务，testlink中还没有以jira号开头的测试计划 或者测试计划中没有添加测试用例，请检查！！！\n\n{}".format(no_testplan)
    print(content)
    wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": list(set(no_testplan_mentioned_list))
        }
    }
    requests.post(wechat_webhook, json=msg)
