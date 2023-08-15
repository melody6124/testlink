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
jql = 'project = ACP AND issuetype = Bug AND BugFoundStage = 发版后阶段 AND resolution not in ("Not a Bug",Rejected,Duplicate,"By Design") AND (labels not in (tencent, 非产品问题,稳定性问题,性能问题,安全问题) OR labels is EMPTY) AND created >= -1w'
issues = jira.search_issues(jql)
no_comment = ""
no_qaowner = ""
no_qabugrootcause = ""
no_comment_mentioned_list = ['jnshi']
no_qaowner_mentioned_list = ['jnshi']
no_rootcause_mentioned_list = ['jnshi']
wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
for i in issues:
    if i.raw['fields']['customfield_11712'] is not None:
        print(i.raw['fields']['customfield_11712'])
        reporter = str(i.raw['fields']['customfield_11712']['displayName'])
        name = i.raw['fields']['customfield_11712']['name']
    else:
        reporter = str(i.fields.reporter)
        name = i.fields.reporter.name
        no_qaowner = no_qaowner + '@{} http://jira.alauda.cn/browse/{} {} \n'.format(reporter, i.key, i.fields.summary)
        no_qaowner_mentioned_list.append(name)
    if i.raw['fields']['customfield_11613'] is None:
        no_qabugrootcause = no_qabugrootcause + '@{} http://jira.alauda.cn/browse/{} {} \n'.format(reporter, i.key, i.fields.summary)
        no_rootcause_mentioned_list.append(name)
    comments = jira.comments(i.key)
    reviewed = False
    for comment in comments:
        # 判断jira comment中是否添加了新增的测试用例编号
        if '复盘原因' in comment.body:
            reviewed = True
            break
        else:
            continue
    if not reviewed:
        no_comment = no_comment + '@{} http://jira.alauda.cn/browse/{} {} \n'.format(reporter, i.key, i.fields.summary)
        no_comment_mentioned_list.append(name)

if no_qaowner != "":
    content = "过去一周发现的【发版后的bug】, 没有QAOwner\n\n{}".format(no_qaowner)
    print(content)
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": list(set(no_qaowner_mentioned_list))
        }
    }
    requests.post(wechat_webhook, json=msg)
if no_qabugrootcause != "":
    content = "过去一周发现的【发版后的bug】, 没有QABugRootCause\n\n{}".format(no_qabugrootcause)
    print(content)
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": list(set(no_rootcause_mentioned_list))
        }
    }
    requests.post(wechat_webhook, json=msg)
if no_comment != "":
    content = "过去一周发现的【发版后的bug】, 没有添加comment:复盘原因 为什么在Affects Version发版前没发现这个bug\n\n{}".format(no_comment)
    print(content)
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": list(set(no_comment_mentioned_list))
        }
    }
    requests.post(wechat_webhook, json=msg)
