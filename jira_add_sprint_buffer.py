from jira import JIRA

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("jnshi", "1021nanjing.?"))
boards = jira.boards(name='Alauda CP 看板')
board_id = boards[0].id
print(board_id)
sprints = jira.sprints(board_id, state='future')  # state='active' state='closed'
print(sprints)
sprint_name = sprints[0].name
sprint_id = sprints[0].id
issue_dict = []
for name in ["myliu", "hlzheng", "yuanshi"]:
    issue_dict.append({'project': "ACP", 'issuetype': {'name': 'Job'}, 'summary': f"{sprint_name}-UI自动化结果分析+修复", 'assignee': {'name': name},
                       'description': "记录每次分析的有效时间（发现开发bug、测试代码bug等,注意关联对应的jira）、无效时间（环境问题、重复分析等)",
                       'customfield_10006': 1, 'labels': ['UI自动化测试发现的bug']})
for name in ["xfzhao", "kewang", "yuanshi"]:  # "jnshi",
    issue_dict.append({'project': "ACP", 'issuetype': {'name': 'Job'}, 'summary': f"{sprint_name}-API自动化结果分析+修复", 'assignee': {'name': name},
                       'description': "记录每次分析的有效时间（发现开发bug、测试代码bug等,注意关联对应的jira）、无效时间（环境问题、重复分析等)",
                       'customfield_10006': 1, 'labels': ['API自动化测试发现的bug']})
for name in ["xfzhao", "myliu", "hlzheng", "kewang", "yuanshi"]:  # "jnshi",
    issue_dict.append({'project': "ACP", 'issuetype': {'name': 'Job'}, 'summary': f"{sprint_name}-开会bug验证等", 'assignee': {'name': name},
                       'customfield_10006': 2})

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

# issues = jira.search_issues(f'labels = UI自动化测试发现的bug AND assignee in (jnshi)')
# for i in issues:
#     print(i)
#     print(i.raw)
#     print(i.raw['fields'])
