# -*- coding: utf-8 -*-
from jira import JIRA
import requests

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = '(project = ACP AND fixVersion in versionMatch("3.6.5$") OR project = Requirements AND issuetype = Requirement AND "Product Version" in ("ACP 3.6.5")) AND (resolution not in ("Not a Bug", Duplicate, "By Design", "won\'t do") OR resolution is EMPTY)'
issues = jira.search_issues(jql)
nocomment = ""
content = ""
mentioned_list = []
for i in issues:
    reporter = str(i.fields.reporter)
    testcaseurl = i.raw['fields']['customfield_12148']
    comments = i.raw['fields']['comment']['comments']
    reviewed = False
    for comment in comments:
        # 判断jira comment中是否添加了新增的测试用例编号
        if '3.6.5验证通过' in comment['body']:
            reviewed = True
            break
        else:
            continue
    if not reviewed:
        nocomment = nocomment + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)

if nocomment != "":
    content = content + "\n没有comment【3.6.5验证通过】，请及时验证并添加comment\n{}".format(nocomment)
# print(content)
# if content != "":
#     wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
#     msg = {
#         "msgtype": "text",
#         "text": {
#             "content": content,
#             "mentioned_list": list(set(mentioned_list))
#         }
#     }
#     requests.post(wechat_webhook, json=msg)
