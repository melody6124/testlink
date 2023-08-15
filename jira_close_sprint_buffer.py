from jira import JIRA

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("jnshi", "1021nanjing.?"))
boards = jira.boards(name='Alauda CP 看板')
board_id = boards[0].id
print(board_id)
sprints = jira.sprints(board_id, state='active')  # state='active' state='closed'
print(sprints)
sprint_name = sprints[0].name
sprint_id = sprints[0].id

keys = []
issues = jira.search_issues(f'project = ACP AND (summary ~ 安全处理 OR summary  ~ 自动化结果分析 OR summary ~开会bug验证等)  AND issuetype = Job AND Sprint = {sprint_id}')
for i in issues:
    keys.append(i.key)
print(keys)
for key in keys:
    # backlog
    jira.transition_issue(key, "151")
    # start
    jira.transition_issue(key, "181")
    # done
    jira.transition_issue(key, "201")

# issues = jira.search_issues(f'labels = UI自动化测试发现的bug AND assignee in (jnshi)')
# for i in issues:
#     print(i)
#     print(i.raw)
#     print(i.raw['fields'])

# transitions = jira.transitions("ACP-26151")
# print(transitions)
# jira.transition_issue("ACP-26151", "181")
# transitions = jira.transitions("ACP-26151")
# print(transitions)
# jira.transition_issue("ACP-26151", "201")
