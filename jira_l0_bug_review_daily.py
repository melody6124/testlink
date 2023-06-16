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
jql = 'project = ACP AND issuetype = Bug AND priority = "L0 - Critical" AND status != Cancelled AND (fixVersion = EMPTY or Sprint is EMPTY) AND created >= -1d order by created DESC'
issues = jira.search_issues(jql)
closed = ""
no_testplan = ""
mentioned_list = []

for i in issues:
    reporter = str(i.fields.reporter)
    mentioned_list.append(i.fields.reporter.name)
    closed = closed + '@{} http://jira.alauda.cn/browse/{} {} \n'.format(reporter, i.key, i.fields.summary)

if closed != "":
    content = "过去一天发现的L0 bug，请及时和开发沟通确认，更新【Fix Version】和【Sprint】\n\n{}".format(closed)
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
