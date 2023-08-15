from jira import JIRA

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("jnshi", "1021jingnan.?"))
jql = 'status not in (Cancelled) AND issuetype in (Bug) AND project = ACP AND created >= -1d'
# status not in (Closed, Done, "Signed Off", Resolved, 已验证, Cancelled, "Ready for QA", "In Testing")
issues = jira.search_issues(jql)
# jira_user_features = {
#     "apps": ['ACP - 集群管理 - 资源管理', 'ACP - 辅助功能', 'ACP - 安全管理 - 节点隔离策略', 'ACP - 应用管理 - OAM应用', 'ACP - 应用管理 - 原生应用', 'ACP - 命名空间概览', 'ACP - 命名空间管理', 'ACP - 联邦命名空间管理',
#              'ACP - 应用管理 - 联邦应用', 'ACP - Workload管理', 'ACP - 配置管理', 'ACP - 自定义资源定义', 'ACP - 超售比', 'ACP - 应用商店管理 - 模板管理', 'ACP - 应用商店管理 - Operator',
#              'ACP - 应用商店管理 - 应用包管理', 'ACP - 应用商店 - 通用功能', 'ACP - 应用商店 - DockerRegistry',
#              'ACP - 应用商店 - ChartMuseum', 'ACP - 应用管理 - 组件应用', 'ACP - 应用管理 - 模板应用', 'ACP - 镜像仓库', 'ACP - 定时任务管理', 'ACP - GitOps应用', 'ACP - 云边协同'],
#     "net": ['ACP - 网络管理 - OVN', 'ACP - 网络管理 - 负载均衡', 'ACP - 网络管理 - GatewayAPI', 'ACP - 网络管理 - 网络监测', 'ACP - 网络管理 - 集群网络策略', 'ACP - 网络管理 - CALICO',
#             'ACP - 网络管理 - Flannel', 'ACP - 网络管理 - 域名证书', 'ACP - 网络管理 - SVC/Ingress', 'ACP - 网络管理 - 外部路由'],
#     "storage": ['ACP - 虚拟化管理', 'ACP - 存储管理 - PV/PVC/StorageClass', 'ACP - 存储管理 - Rook-Ceph', 'ACP - 存储管理 - Topolvm', 'ACP - 存储管理 - 对接外部存储', 'ACP - 存储管理 - Minio',
#                 'ACP - 功能开关']
# }
for i in issues:
    labels = i.fields.labels
    if 'net' in labels or 'apps' in labels or 'storage' in labels:
        pass
    else:
        features = i.raw['fields']['customfield_12300']
        # if "value" in str(features):
        feature = features['value']
        if "虚拟化管理" in feature or "存储管理" in feature:
            labels.append('storage')
        elif "网络管理" in feature:
            labels.append('net')
        else:
            labels.append('apps')
        # if feature in jira_user_features['apps']:
        #     labels.append('apps')
        # elif feature in jira_user_features['net']:
        #     labels.append('net')
        # elif feature in jira_user_features['storage']:
        #     labels.append('storage')
        issue = jira.issue(i.key)
        issue.update(fields={'labels': labels})
