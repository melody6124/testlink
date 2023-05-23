# -*- coding: utf-8 -*-
import requests
from jira import JIRA

from division import en_chs, mentions

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = 'project = ACP AND issuetype = Improvement AND status = Resolved AND IsTestCaseChanged = 需要修改测试用例 AND created >= 2022-06-01 ORDER BY created DESC'
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
    reporter = ""
    changelog_response = requests.get('https://jira.alauda.cn/rest/api/2/search?jql=key=' + i.key + '&expand=changelog&fields=""',
                                      auth=("yuzhou", "zhouyu0401"))
    json_issue_changelog = changelog_response.json()['issues'][0]['changelog']['histories']
    for history in json_issue_changelog:
        author = history['author']['displayName']
        for item in history['items']:
            if item['toString'] == 'Pass Test':
                reporter = author
                break
    testcaseurl = i.raw['fields']['customfield_12148']
    if "http://testlink.alauda.cn/linkto.php?tprojectPrefix" not in str(testcaseurl):
        if reporter in list(en_ch.keys()):
            notestcaseurl = notestcaseurl + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
            notestcaseurl_mentioned_list.append(mention[reporter])
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
                nocomment = nocomment + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)
                nocomment_mentioned_list.append('jnshi')

if notestcaseurl != "":
    content = "已关闭的Improvement中需要修改测试用例:TestCaseURL没有填写或错误链接，请补充并发起用例评审;确认无需修改测试用例，请更新IsTestCaseChanged\n\n{}".format(notestcaseurl)
    print(content)
    send(content, notestcaseurl_mentioned_list)
if nocomment != "":
    content = "Improvement关闭时，没有按流程进行用例评审，请及时添加comment【用例评审通过】\n参考流程 https://confluence.alauda.cn/pages/releaseview.action?pageId=75094349\n\n{}".format(
        nocomment)
    print(content)
    send(content, nocomment_mentioned_list)
