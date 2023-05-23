# -*- coding: utf-8 -*-
import requests
from jira import JIRA

from division import jira_user_features, en_chs, mentions

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = 'project = ACP AND QABugRootCause = 测试用例很难cover AND created >= -7d ORDER BY key DESC'
issues = jira.search_issues(jql)
en_ch = en_chs
mention = mentions
user_features = jira_user_features
notestcaseurl = ""
nocomment = ""
content = ""
mentioned_list = []
for i in issues:
    reporter = str(i.fields.reporter)
    if reporter in list(en_ch.keys()):
        notestcaseurl = notestcaseurl + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
        mentioned_list.append(mention[reporter])
    else:
        features = i.raw['fields']['customfield_12300']
        if "value" in str(features):
            feature = features['value']
            flag = False
            for user_feature in user_features:
                user = list(user_feature.keys())[0]
                if feature in user_feature[user]:
                    notestcaseurl = notestcaseurl + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[user], i.key, i.fields.summary)
                    mentioned_list.append(mention[user])
                    flag = True
                    break
            if not flag:
                notestcaseurl = notestcaseurl + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)
        else:
            notestcaseurl = notestcaseurl + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)

if notestcaseurl != "":
    content = "过去一周QABugRootCause = 测试用例很难cover的jira需要review是否是真的难cover\n{}".format(notestcaseurl)
else:
    content = "恭喜恭喜!!!过去一周没有QABugRootCause = 测试用例很难cover的jira需要review"

print(content)
if content != "":
    mentioned_list.append('jnshi')
    wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": list(set(mentioned_list))
        }
    }
    requests.post(wechat_webhook, json=msg)
