# -*- coding: utf-8 -*-
import requests
from jira import JIRA

from division import mentions, en_chs

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = 'project = ACP AND summary ~ 测试用例设计 AND status = Resolved  AND resolutiondate >= 2023-01-01 ORDER BY resolutiondate  DESC'
issues = jira.search_issues(jql)
en_ch = en_chs
mention = mentions
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
    reporter = i.fields.assignee.displayName
    testcaseurl = i.raw['fields']['customfield_12406']
    if "http://testlink.alauda.cn" not in str(testcaseurl) \
            and "https://edge.alauda.cn/console-devops/workspace" not in str(testcaseurl):
        notestcaseurl = notestcaseurl + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
        notestcaseurl_mentioned_list.append(mention[reporter])
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
            nocomment = nocomment + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
            nocomment_mentioned_list.append(mention[reporter])

if notestcaseurl != "":
    content = "测试用例设计任务关闭时，Output URL没有填写或错误链接，请补充并发起用例评审\n{}".format(notestcaseurl)
    print(content)
    send(content, notestcaseurl_mentioned_list)

if nocomment != "":
    content = "测试用例设计任务关闭时，没有按流程进行用例评审，请及时添加comment【用例评审通过】\n参考流程 https://confluence.alauda.cn/pages/releaseview.action?pageId=75094349\n\n{}".format(
        nocomment)
    print(content)
    send(content, nocomment_mentioned_list)
