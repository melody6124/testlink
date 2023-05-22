# -*- coding: utf-8 -*-
import datetime

import requests

# from jira import JIRA
#
# jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
# users = jira.group_members('test')
# origin_users = list(users.keys())
origin_users = ['jnshi', 'kewang', 'xfzhao', 'myliu', 'yuanshi', 'hlzheng']
basic_auth = ("yuzhou", "zhouyu0401")
users_url = "https://jira.alauda.cn/rest/tempo-core/1/users/search"
users_payload = {"keys": origin_users}
users_ret = requests.post(url=users_url, json=users_payload, auth=basic_auth)
users = []
userKeys = []
for user in users_ret.json()['results']:
    users.append({"key": user['key'], "displayName": user['displayName'], "name": user['jiraUser']['name'], "time": 0})
    userKeys.append(user['key'])
fromdate = datetime.date.today()
delta = datetime.timedelta(days=1)
todate = fromdate + delta
worklogs_url = "https://jira.alauda.cn/rest/tempo-timesheets/4/worklogs/search"
worklogs_payload = {"from": str(fromdate), "to": str(todate), "worker": userKeys}  # "projectKey": ["ACP"]
worklogs_ret = requests.post(url=worklogs_url, json=worklogs_payload, auth=basic_auth)

for worklog in worklogs_ret.json():
    for user in users:
        if worklog['worker'] == user['key']:
            user['time'] = user['time'] + worklog['timeSpentSeconds']
print(users)
errors = []
for user in users:
    if user['time'] < 27000:
        errors.append(user['name'])
wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
if errors:
    msg = {
        "msgtype": "text",
        "text": {
            "content": "{} logtime总时长不足7.5小时,请及时补充".format(fromdate),
            "mentioned_list": errors
        }
    }
else:
    msg = {
        "msgtype": "text",
        "text": {
            "content": "恭喜恭喜，logtime总时长都满7.5小时了"
        }
    }
requests.post(wechat_webhook, json=msg)
