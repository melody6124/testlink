# -*- coding: utf-8 -*-
import requests
from jira import JIRA

jira = JIRA(server="https://jira.alauda.cn", basic_auth=("yuzhou", "zhouyu0401"))
jql = 'project = ACP AND QABugRootCause = 测试用例很难cover AND created >= -7d ORDER BY key DESC'
issues = jira.search_issues(jql)
en_ch = {"Jingnan Shi": "史京南", "Hulin Zheng": "郑虎林", "Ke Wang": "王珂", "Yuan Shi": "施源", "Mingyu Liu": "刘明宇",
         "Xiaofeng Zhao": "赵晓峰", "Junlei Li": "李俊磊", "Ya Wei": "魏娅", "Zhongxiu Zhang": "张仲秀"}
mention = {"Jingnan Shi": "jnshi", "Hulin Zheng": "hlzheng", "Ke Wang": "kewang", "Yuan Shi": "yuanshi", "Mingyu Liu": "myliu",
           "Xiaofeng Zhao": "xfzhao", "Junlei Li": "jlli", "Ya Wei": "yawei", "Zhongxiu Zhang": "zxzhang"}
user_features = [
    {"Hulin Zheng": ['ACP - 命名空间概览', 'ACP - 命名空间管理', 'ACP - 联邦命名空间管理', 'ACP - 联邦应用管理', 'ACP - Workload管理', 'ACP - 配置管理', 'ACP - GPU', 'ACP - 自定义资源定义']},
    {"Jingnan Shi": ['ACP - 集群管理 - 资源管理', 'ACP - 辅助功能', 'ACP - 安全管理 - 节点隔离策略', 'ACP - OAM应用管理', 'ACP - 原生应用管理']},
    {"Ke Wang": ['ACP - 网络管理 - OVN', 'ACP - 网络管理 - 负载均衡', 'ACP - 网络管理 - GatewayAPI', 'ACP - 网络管理 - 网络监测', 'ACP - 网络管理 - 集群网络策略']},
    {"Yuan Shi": ['ACP - 网络管理 - CALICO', 'ACP - 网络管理 - Flannel', 'ACP - 网络管理 - 域名证书', 'ACP - 网络管理 - SVC/Ingress', 'ACP - 网络管理 - 外部路由', 'ACP - 虚拟化管理']},
    {"Mingyu Liu": ['ACP - 存储管理 - PV/PVC/StorageClass', 'ACP - 存储管理 - Rook-Ceph', 'ACP - 存储管理 - Topolvm', 'ACP - 存储管理 - 对接外部存储', 'ACP - 超售比',
                    'ACP - 功能开关']},
    {"Xiaofeng Zhao": ['ACP - 应用商店管理 - 模板管理', 'ACP - 应用商店管理 - Operator', 'ACP - 应用商店 - 通用功能', 'ACP - 应用商店 - DockerRegistry', 'ACP - 应用商店 - ChartMuseum',
                       'ACP - 组件应用管理', 'ACP - 镜像仓库', 'ACP - 定时任务管理', 'ACP - GitOps应用', 'ACP - 云边协同']}
]
notestcaseurl = ""
nocomment = ""
content = ""
mentioned_list = []
for i in issues:
    reporter = str(i.fields.reporter)
    if reporter in list(en_ch.keys()):
        notestcaseurl = notestcaseurl + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[reporter], i.key, i.fields.summary)
        mentioned_list.append(mention[reporter])
    else:
        features = i.raw['fields']['customfield_12300']
        if "value" in str(features):
            feature = features['value']
            flag = False
            for user_feature in user_features:
                user = list(user_feature.keys())[0]
                if feature in user_feature[user]:
                    notestcaseurl = notestcaseurl + "@{} http://jira.alauda.cn/browse/{} {} \n".format(en_ch[user], i.key, i.fields.summary)
                    mentioned_list.append(mention[user])
                    flag = True
                    break
            if not flag:
                notestcaseurl = notestcaseurl + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)
        else:
            notestcaseurl = notestcaseurl + "http://jira.alauda.cn/browse/{} {} \n".format(i.key, i.fields.summary)

if notestcaseurl != "":
    content = "过去一周QABugRootCause = 测试用例很难cover的jira需要review是否是真的难cover\n{}".format(notestcaseurl)
else:
    content = "恭喜恭喜!!!过去一周没有QABugRootCause = 测试用例很难cover的jira需要review"

print(content)
if content != "":
    mentioned_list.append('jnshi')
    wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": list(set(mentioned_list))
        }
    }
    requests.post(wechat_webhook, json=msg)
