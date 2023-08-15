# -*- coding: utf-8 -*-
import requests
from jira import JIRA

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = '(project in (Development, ACP, "Alauda Service Mesh", "Alauda Infrastructure", "Alauda DevOps", MiddleWare) AND fixVersion in versionMatch("3.12.2$") OR project = Requirements AND issuetype = Requirement AND ProductVersion in (v3.12.2)) AND (resolution not in ("Not a Bug", Duplicate, "By Design", "won\'t do","Cannot Reproduce",Unresolved))  AND assignee not in membersOf(test) AND project = ACP AND issuetype != Improvement  AND issuetype != Document'
issues = jira.search_issues(jql)
nocomment = ""
content = ""
mentioned_list = []
for i in issues:
    reporter = str(i.fields.reporter)
    mentioned = i.fields.reporter.name
    testcaseurl = i.raw['fields']['customfield_12148']
    comments = jira.comments(i.key)
    reviewed = False
    for comment in comments:
        # 判断jira comment中是否添加了新增的测试用例编号
        if '3.12.2验证通过' in comment.body:
            reviewed = True
            break
        else:
            continue
    if not reviewed:
        nocomment = nocomment + "@{} http://jira.alauda.cn/browse/{} {} \n".format(reporter, i.key, i.fields.summary)
        mentioned_list.append(mentioned)

if nocomment != "":
    content = content + "没有comment【3.12.2验证通过】，请及时验证并添加comment\n\n{}".format(nocomment)
print(content)
if content != "":
    wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": list(set(mentioned_list))
        }
    }
    requests.post(wechat_webhook, json=msg)
