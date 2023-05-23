# -*- coding: utf-8 -*-
import requests
from jira import JIRA

from division import jira_user_features, en_chs, mentions

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = 'project = ACP AND issuetype in (Bug, Improvement) AND  status in ("Ready for QA", "In Testing", "Ready for Doc Review") AND fixVersion not in ("v3.8.2-isdp","v3.8.2-isdp-1","v3.8.2-isdp-2","v3.8.2-isdp-3") ORDER BY reporter ASC, status ASC'
issues = jira.search_issues(jql)
en_ch = en_chs
mention = mentions
user_features = jira_user_features
ing_version = "v3.10.3"
future_version = "v3.13"
ing_us = ""
future_us = ""
us = ""

other = ""
mentioned_list = []
for i in issues:
    fixversion = str(i.raw['fields']['fixVersions'][0]['name'])
    reporter = str(i.fields.reporter)
    if reporter in list(en_ch.keys()):
        if ing_version in fixversion:
            ing_us = ing_us + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
        elif future_version in fixversion:
            future_us = future_us + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
        else:
            us = us + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
        mentioned_list.append(mention[reporter])
    else:
        features = i.raw['fields']['customfield_12300']
        if "value" in str(features):
            feature = features['value']
            flag = False
            for user_feature in user_features:
                user = list(user_feature.keys())[0]
                if feature in user_feature[user]:
                    if ing_version in fixversion:
                        ing_us = ing_us + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[user], i.key, i.fields.summary)
                    elif future_version in fixversion:
                        future_us = future_us + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[user], i.key, i.fields.summary)
                    else:
                        us = us + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[user], i.key, i.fields.summary)
                    mentioned_list.append(mention[user])
                    flag = True
                    break
            if not flag:
                other = other + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)
                mentioned_list.append('jnshi')
        else:
            other = other + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)
            mentioned_list.append('jnshi')
content = ""
if ing_us != "":
    content = content + "\n正在发版的 {} Ready for QA的bug,请及时验证\n{}".format(ing_version, ing_us)
if future_us != "":
    content = content + "\n即将发版的 {} Ready for QA的bug,请及时验证\n{}".format(future_version, future_us)
if us != "":
    content = content + "\n其他版本的 Ready for QA的bug,请及时验证\n{}".format(us)
if other != "":
    content = content + "\n其他人发现的bug,需要安排测试 @史京南\n{}".format(other)
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
