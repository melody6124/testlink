# -*- coding: utf-8 -*-
import requests
from jira import JIRA

from division import jira_user_features, mentions, en_chs

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = 'project = ACP AND issuetype = Bug AND resolution in (Unresolved, "Pass Test", Done, "By Design") AND QABugRootCause in (基本测试用例遗漏, 测试用例很难cover,测试用例设计错误) AND created >= 2023-01-01 ORDER BY created DESC'
issues = jira.search_issues(jql)
en_ch = en_chs
mention = mentions
user_features = jira_user_features
notestcaseurl = ""
nocomment = ""
content = ""
notestcaseurl_mentioned_list = []
nocomment_mentioned_list = []


def send(content, mentioned_list):
    wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
    if content != "":
        msg = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": list(set(mentioned_list))
            }
        }
        requests.post(wechat_webhook, json=msg)


for i in issues:
    reporter = str(i.fields.reporter)
    testcaseurl = i.raw['fields']['customfield_12148']
    if "http://testlink.alauda.cn/linkto.php?tprojectPrefix" not in str(testcaseurl):
        if reporter in list(en_ch.keys()):
            notestcaseurl = notestcaseurl + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
            notestcaseurl_mentioned_list.append(mention[reporter])
        else:
            features = i.raw['fields']['customfield_12300']
            if "value" in str(features):
                feature = features['value']
                flag = False
                for user_feature in user_features:
                    user = list(user_feature.keys())[0]
                    if feature in user_feature[user]:
                        notestcaseurl = notestcaseurl + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[user], i.key, i.fields.summary)
                        notestcaseurl_mentioned_list.append(mention[user])
                        flag = True
                        break
                if not flag:
                    notestcaseurl = notestcaseurl + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)
                    notestcaseurl_mentioned_list.append('jnshi')
            else:
                notestcaseurl = notestcaseurl + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)
                notestcaseurl_mentioned_list.append('jnshi')
    else:
        comments = jira.comments(i.key)
        reviewed = False
        for comment in comments:
            if '用例评审通过' in comment.body:
                reviewed = True
                break
            else:
                continue
        if not reviewed:
            if reporter in list(en_ch.keys()):
                nocomment = nocomment + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
                nocomment_mentioned_list.append(mention[reporter])
            else:
                features = i.raw['fields']['customfield_12300']
                if "value" in str(features):
                    feature = features['value']
                    flag = False
                    for user_feature in user_features:
                        user = list(user_feature.keys())[0]
                        if feature in user_feature[user]:
                            nocomment = nocomment + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[user], i.key, i.fields.summary)
                            nocomment_mentioned_list.append(mention[user])
                            flag = True
                            break
                    if not flag:
                        nocomment = nocomment + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)
                        nocomment_mentioned_list.append('jnshi')
                else:
                    nocomment = nocomment + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)
                    nocomment_mentioned_list.append('jnshi')

if notestcaseurl != "":
    content = "【基本测试用例遗漏、测试用例很难cover、测试用例设计错误】:TestCaseURL没有补充或者错误链接，请补充并发起用例评审\n\n{}".format(notestcaseurl)
    print(content)
    send(content, notestcaseurl_mentioned_list)
if nocomment != "":
    content = "Bug关闭时，没有按流程进行用例评审，请及时添加comment【用例评审通过】\n参考流程 https://confluence.alauda.cn/pages/releaseview.action?pageId=75094349\n\n{}".format(nocomment)
    print(content)
    send(content, nocomment_mentioned_list)
