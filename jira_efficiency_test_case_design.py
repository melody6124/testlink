import requests
import testlink
from jira import JIRA


def send_content_error_output(results):
    contents = ""
    if results:
        contents = "测试用例设计jira关闭时，Output URL为空，请检查！！！\n"
    for result in results:
        contents = contents + "@{} {}:{} \n".format(result['name'], result['id'], result['summary'])
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


def send_content_no_testplan(results):
    contents = ""
    if results:
        contents = "测试用例设计jira关闭时，testlink中还没有以关联测试任务的jira号开头的测试计划 或者测试计划中没有添加测试用例，请检查！！！\n"
    for result in results:
        contents = contents + "@{} {}:{} \n".format(result['name'], result['id'], result['summary'])
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
        contents = "测试用例设计jira关闭时，没有logtime，请检查！！！\n"
    for result in results:
        contents = contents + "@{} {}:{} \n".format(result['name'], result['id'], result['summary'])
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
        contents = "测试用例设计jira关闭后的成本统计，请参考\n"
    for result in results:
        contents = contents + "{} {}:{} 用例总数 {} 花费时间 {}h 平均时间 {}h\n".format(result['name'], result['id'], result['summary'], result['case_total'],
                                                                            result['timespent'] / 60 / 60,
                                                                            '%.2f' % (result['timespent'] / result['case_total'] / 60 / 60))
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


url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = '7ccbcfc2d1c580277d7b5ce1038c9ee6'

tlc = testlink.TestlinkAPIClient(url, key)
test_project_name = "ACP-master"
testproject_id = tlc.getProjectIDByName(test_project_name)

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = 'project = ACP AND summary ~ 测试用例设计 AND assignee in (membersOf(test))  AND status = Resolved AND resolved >= 2023-01-01 ORDER BY assignee ASC,resolutiondate DESC'
issues = jira.search_issues(jql)
error_output = []
no_testplan = []
no_logtime = []
timespents = []
plans = tlc.getProjectTestPlans(testproject_id)
for i in issues:
    id = i.key
    summary = i.fields.summary
    summary_name = summary.split(' - ')[0].rstrip()
    print(summary_name)
    assign = i.fields.assignee.name
    output = i.raw['fields']['customfield_12406']
    timespent = i.fields.timespent
    if timespent is None:
        no_logtime.append({'name': assign, 'id': id, 'summary': summary})
    if output is None:
        error_output.append({'name': assign, 'id': id, 'summary': summary})
    plan_name = ''
    for plan in plans:
        if id in plan['name'] or summary_name in plan['name']:
            plan_name = plan['name']
            break
    if plan_name == '':
        no_testplan.append({'name': assign, 'id': id, 'summary': summary})
    else:
        testplanid = tlc.getTestPlanByName(test_project_name, plan_name)[0]['id']
        case_total = int(tlc.getTotalsForTestPlan(testplanid)['total'][0]['qty'])
        if case_total == 0:
            no_testplan.append({'name': assign, 'id': id, 'summary': summary})
        else:
            if timespent is not None:
                timespents.append({'name': assign, 'id': id, 'summary': summary, 'output': output, 'timespent': timespent, 'case_total': case_total})

send_content_error_output(error_output)
send_content_no_testplan(no_testplan)
send_content_no_logtime(no_logtime)
send_content_timespents(timespents)
