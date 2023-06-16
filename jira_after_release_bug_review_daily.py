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
jql = 'project = ACP AND issuetype = Bug AND resolution not in ("Not a Bug",Rejected,Duplicate,"By Design") AND BugFoundStage = 发版后阶段 AND resolved >= -1d'
issues = jira.search_issues(jql)
closed = ""
no_testplan = ""
mentioned_list = ['jnshi']

for i in issues:
    if i.raw['fields']['customfield_11712'] is not None:
        print(i.raw['fields']['customfield_11712'])
        reporter = str(i.raw['fields']['customfield_11712']['displayName'])
        mentioned_list.append(i.raw['fields']['customfield_11712']['name'])
    else:
        reporter = str(i.fields.reporter)
        mentioned_list.append(i.fields.reporter.name)
    closed = closed + '@{} http://jira.alauda.cn/browse/{} {} \n'.format(reporter, i.key, i.fields.summary)

if closed != "":
    content = "过去一天发现的【发版后的bug】, 请更新QAOwner、QABugRootCause并且添加comment【复盘原因】：为什么在Affects Version发版前没发现这个bug\n\n{}".format(closed)
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
