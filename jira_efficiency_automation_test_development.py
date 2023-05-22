import re

import gitlab
import requests
from jira import JIRA


def send_content_error_output(results):
    contents = ""
    if results:
        contents = "<font color=\"warning\">自动化测试开发jira关闭时，Output URL为空或者不是gitlab的pr链接，请检查！！！ </font>\n"
    for result in results:
        contents = contents + '@{} [{}](http://jira.alauda.cn/browse/{}) {} \n'.format(result['name'], result['id'], result['id'], result['summary'])
    print(contents)
    if contents != "":
        wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
        msg = {
            "msgtype": "markdown",
            "markdown": {
                "content": contents,
            }
        }
        requests.post(wechat_webhook, json=msg)


def send_content_no_logtime(results):
    contents = ""
    if results:
        contents = "<font color=\"warning\">自动化测试开发jira关闭时，没有logtime，请检查！！！ </font>\n"
    for result in results:
        contents = contents + '@{} [{}](http://jira.alauda.cn/browse/{}) {} \n'.format(result['name'], result['id'], result['id'], result['summary'])
    print(contents)
    if contents != "":
        wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
        msg = {
            "msgtype": "markdown",
            "markdown": {
                "content": contents,
            }
        }
        requests.post(wechat_webhook, json=msg)


def send_content_timespents(results):
    contents = ""
    if results:
        contents = "<font color=\"info\">自动化测试开发jira关闭后的成本统计，请参考 </font>\n"
    for result in results:
        contents = contents + '@{} [{}](http://jira.alauda.cn/browse/{}) {}\n完成日期 {} 用例数 {} 花费时间 {}h 平均时间<font color=\"warning\"> {}</font>h \n' \
            .format(result['name'], result['id'], result['id'], result['summary'].replace(" ", ''), result['resolutiondate'],
                    result['case_total'], result['timespent'] / 60 / 60,
                    '%.2f' % (result['timespent'] / 60 / 60 / result['case_total']) if result['case_total'] > 0 else "ERROR")
    print(contents)
    if contents != "":
        wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=7b61450b-5a61-4bb1-9539-8e993218d5f7"
        msg = {
            "msgtype": "markdown",
            "markdown": {
                "content": contents,
            }
        }
        requests.post(wechat_webhook, json=msg)


jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
boards = [(item.id, item.name) for item in jira.boards()]
board_id = 0
for item in boards:
    if item[1] == 'Alauda CP 看板':
        board_id = item[0]
        break
# sprints = jira.sprints(board_id, state='active')
# print("当前sprint{}".format(sprints))
# closed_sprint_id = sprints[0].id - 1
jql = f'project = ACP AND (summary ~ 自动化测试开发 or summary ~ 补充自动化任务) AND assignee in (membersOf(test))  AND status = Resolved AND resolved >= 2023-01-01 ORDER BY assignee ASC,resolutiondate DESC'
issues = jira.search_issues(jql)
error_output = []
no_logtime = []
timespents = []

gitlab_url = "https://gitlab-ce.alauda.cn"
token = "S41n3-D1eWzEEJ6sGYvg"
gl = gitlab.Gitlab(url=gitlab_url, private_token=token)

for i in issues:
    id = i.key
    # resolved_data = i.fields
    summary = i.fields.summary
    summary_name = summary.split(' - ')[0].rstrip()
    assign = i.fields.assignee
    output = i.raw['fields']['customfield_12406']
    resolutiondate = i.raw['fields']['resolutiondate'].split('T')[0]
    timespent = i.fields.timespent
    if timespent is None:
        no_logtime.append({'name': assign, 'id': id, 'summary': summary})
    else:
        if output is None or 'merge_requests' not in output:
            error_output.append({'name': assign, 'id': id, 'summary': summary})
        else:
            pr = re.findall('merge_requests/[0-9]{2,6}', output)[0].split('/')[1]
            gitlab_url = "https://gitlab-ce.alauda.cn"
            token = "S41n3-D1eWzEEJ6sGYvg"
            gl = gitlab.Gitlab(url=gitlab_url, private_token=token)
            # projects = gl.projects.list(search='guardian')
            # print(projects)
            # <Project id:159 path_with_namespace:alaudatest/ares><Project id:1025 path_with_namespace:frontend/guardian>
            if 'ares' in output:
                project_id = 159
                project = gl.projects.get(project_id)
                repo = 'ares'
            else:
                project_id = 1025
                project = gl.projects.get(project_id)
                repo = 'guardian'
            detail = project.mergerequests.get(pr)
            minus = []
            plus = []
            sha = detail.changes()['sha']
            for change in detail.changes()['changes']:
                if change['diff'] != '':
                    diffs = change['diff'].split('\n')
                    for diff in diffs:
                        if diff.startswith('-'):
                            if repo == 'ares':
                                minus.extend(list(set(re.findall('[0-9]{2,6}_', diff))))
                            else:
                                minus.extend(list(set(re.findall('ACP-[0-9]{2,6}', diff))))
                        elif diff.startswith('+'):
                            if repo == 'ares':
                                plus.extend(list(set(re.findall('[0-9]{2,6}_', diff))))
                            else:
                                plus.extend(list(set(re.findall('ACP-[0-9]{2,6}', diff))))
                else:
                    if change['new_file']:
                        new_path = change['new_path']
                        f = project.files.get(file_path=new_path, ref=sha)
                        file_content = f.decode().decode()
                        diffs = file_content.split('\n')
                        for diff in diffs:
                            if repo == 'ares':
                                plus.extend(list(set(re.findall('[0-9]{2,6}_', diff))))
                            else:
                                plus.extend(list(set(re.findall('ACP-[0-9]{2,6}', diff))))
            timespents.append({'name': assign, 'id': id, 'summary': summary, 'output': output, 'resolutiondate': resolutiondate,
                               'timespent': timespent, 'case_total': len(list(set(plus))) - len(list(set(minus)))})

send_content_error_output(error_output)
send_content_no_logtime(no_logtime)
send_content_timespents(timespents)
