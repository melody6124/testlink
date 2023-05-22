from jira import JIRA

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("jnshi", "1021nanjing.?"))
boards = [(item.id, item.name) for item in jira.boards()]
board_id = 0
for item in boards:
    if item[1] == 'Alauda CP 看板':
        board_id = item[0]
        break
sprints = jira.sprints(board_id, state='future')  # state='active' state='closed'
print(sprints)
sprint_name = sprints[0].name
sprint_id = sprints[0].id
issue_dict = []
for name in ["zyfan"]:
    issue_dict.append({'project': "ACP", 'issuetype': {'name': 'Job'}, 'summary': f"{sprint_name}-Buffer", 'assignee': {'name': name}, 'customfield_10006': 1})
print(issue_dict)
ret = jira.create_issues(field_list=issue_dict)
print(ret)
keys = []
for result in ret:
    i = result['issue']
    print(i)
    keys.append(i.key)
print(keys)
jira.add_issues_to_sprint(sprint_id, keys)
