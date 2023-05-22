# -*- coding:utf-8 -*-
import testlink

url = "http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php"
key = "7ccbcfc2d1c580277d7b5ce1038c9ee6"
testproject_name = "ACP-3.8.x"
testplan_name = "acp3.8.2第一轮测试"
parent_suite = "容器平台"

# case_importance = ("3")  # # high 对应 3，medium 对应 2，low 对应 1
suite_assign = [
    # 核心功能
    {"suitename": "业务视图-OAM 应用", "user": "jnshi", "case_importance": ("3")},
    {"suitename": "业务视图-应用管理>原生应用", "user": "jnshi", "case_importance": ("3")},
    {"suitename": "业务视图-应用管理>模板应用", "user": "xfzhao", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>部署", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>守护进程集", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>有状态副本集", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>定时任务", "user": "xfzhao", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>任务", "user": "xfzhao", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>容器组", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>扩缩容", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>通用-镜像选择组件", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>通用-容器组表单", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>通用-详情页组件", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>通用-容器组列表", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>通用-局部更新", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-配置", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-网络>内部路由", "user": "yuanshi", "case_importance": ("3")},
    {"suitename": "业务视图-网络>入站规则", "user": "yuanshi", "case_importance": ("3")},
    {"suitename": "业务视图-网络>负载均衡", "user": "kewang", "case_importance": ("3")},
    {"suitename": "业务视图-存储>持久卷声明", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "独立视图-应用商店", "user": "xfzhao", "case_importance": ("3")},
    {"suitename": "业务视图-应用目录", "user": "xfzhao", "case_importance": ("3")},
    {"suitename": "平台管理-超售比", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "平台管理-网络管理>域名", "user": "yuanshi", "case_importance": ("3")},
    {"suitename": "平台管理-网络管理>证书", "user": "yuanshi", "case_importance": ("3")},
    {"suitename": "平台管理-网络管理>负载均衡", "user": "kewang", "case_importance": ("3")},
    {"suitename": "平台管理-网络管理>子网>calico", "user": "yuanshi", "case_importance": ("3")},
    {"suitename": "平台管理-网络管理>子网>ovn", "user": "kewang", "case_importance": ("3")},
    {"suitename": "平台管理-存储管理>持久卷", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "平台管理-存储管理>存储类", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "平台管理-存储管理>分布式存储", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "平台管理-存储管理>本地存储", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "平台管理-存储管理>存储相关方案case", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "平台管理-应用商店管理>Operator", "user": "xfzhao", "case_importance": ("3")},
    {"suitename": "项目管理-命名空间>命名空间", "user": "myliu", "case_importance": ("3")},
    # 标准功能
    {"suitename": "业务视图-应用管理>组件应用", "user": "xfzhao", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>gpu", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>asm-acp融合", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-计算组件>通用-debug", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-虚拟化", "user": "yuanshi", "case_importance": ("3")},
    {"suitename": "业务视图-网络>外部路由", "user": "yuanshi", "case_importance": ("3")},
    {"suitename": "业务视图-网络>网络策略", "user": "kewang", "case_importance": ("3")},
    {"suitename": "平台管理-网络管理>集群网络策略", "user": "kewang", "case_importance": ("3")},
    {"suitename": "业务视图-存储> 存储桶声明", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "业务视图-镜像仓库", "user": "xfzhao", "case_importance": ("3")},
    {"suitename": "平台管理-集群管理-资源管理", "user": "jnshi", "case_importance": ("3")},
    {"suitename": "平台管理-存储管理>存储桶", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "平台管理-虚拟化管理", "user": "yuanshi", "case_importance": ("3")},
    {"suitename": "平台管理-安全管理", "user": "jnshi", "case_importance": ("3")},
    # 辅助功能
    {"suitename": "项目管理-命名空间>命名空间概览", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-应用管理>联邦应用", "user": "myliu", "case_importance": ("3")},
    {"suitename": "业务视图-辅助功能", "user": "jnshi", "case_importance": ("3")},
    {"suitename": "平台管理-集群管理-自定义资源", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "平台管理-ovn集群互通管理", "user": "kewang", "case_importance": ("3")},
    {"suitename": "平台管理-kubeOVN网络可视化", "user": "kewang", "case_importance": ("3")},
    {"suitename": "平台管理-网络管理>网络检测", "user": "kewang", "case_importance": ("3")},
    {"suitename": "平台管理-存储管理>卷快照", "user": "bxliu", "case_importance": ("3")},
    {"suitename": "平台管理-应用商店管理>模板仓库", "user": "xfzhao", "case_importance": ("3")},
    {"suitename": "项目管理-命名空间>联邦命名空间", "user": "myliu", "case_importance": ("3")},
]
tlc = testlink.TestlinkAPIClient(url, key)

testproject_id = tlc.getProjectIDByName(testproject_name)
testproject_prefix = tlc.getTestProjectByName(testproject_name)["prefix"]
testplan_id = tlc.getTestPlanByName(testproject_name, testplan_name)[0]["id"]
build_id = tlc.getLatestBuildForTestPlan(testplan_id)["id"]

parent_id = tlc.getTestSuite(parent_suite, testproject_prefix)[0]["id"]
print(f"容器平台的二级目录ID:{parent_id}")

for assign in suite_assign:
    suites = assign["suitename"].split(">")
    global testsuite_id
    testsuite_id = parent_id
    for index, suite in enumerate(suites):
        if index <= len(suites) - 1:
            test_suites = tlc.getTestSuitesForTestSuite(testsuite_id)
            for test_suite in list(test_suites.values()):
                if suite == test_suite["name"]:
                    testsuite_id = test_suite["id"]
                    break
    if testsuite_id == parent_id:
        print(f"当前路径不存在{assign}")
        continue
    testcases = tlc.getTestCasesForTestSuite(testsuiteid=testsuite_id, deep=True, details="full")
    add_case_num = 0
    for testcase in testcases:
        external_id = testcase["external_id"]
        importance = testcase["importance"]
        if importance in assign["case_importance"]:
            add_case_num += 1
            tlc.addTestCaseToTestPlan(testprojectid=testproject_id, testplanid=testplan_id,
                                      testcaseexternalid=external_id,
                                      version=1)
            tlc.assignTestCaseExecutionTask(user=assign["user"], testplanid=testplan_id, testcaseexternalid=external_id,
                                            buildid=build_id)
    if add_case_num == 0:
        print(f"{suites}没有对应的case")
