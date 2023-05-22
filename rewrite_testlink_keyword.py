# -*- coding:utf-8 -*-
import os

import testlink

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = '7ccbcfc2d1c580277d7b5ce1038c9ee6'

tlc = testlink.TestlinkAPIClient(url, key)
test_project_name = os.getenv("PROJECT_TESTLINK", "ACP-master")
testproject_prefix = tlc.getTestProjectByName(test_project_name)["prefix"]
testproject_id = tlc.getProjectIDByName(test_project_name)
testsuite_id = tlc.getTestSuite("容器平台", testproject_prefix)[0]["id"]
subsuites = tlc.getTestSuitesForTestSuite(testsuiteid=testsuite_id)
for subsuite in subsuites.values():
    subsuite_id = subsuite["id"]
    cases = tlc.getTestCasesForTestSuite(testsuiteid=subsuite_id, deep=True, details='full')
    for case in cases:
        id = case["external_id"]
        execution_type = case['execution_type']
        execution_type_ui = tlc.getTestCaseCustomFieldDesignValue(testcaseexternalid=id, version=int(case['version']), testprojectid=testproject_id,
                                                                  customfieldname="execution_type_ui")
        keyword = tlc.getTestCaseKeywords(testcaseexternalid=id)
        if keyword[id] != '':
            keywords = list(keyword[id].values())
        else:
            keywords = []
        #  UI自动化实现的 去掉ui_no_automation
        if execution_type_ui == 'Automated':
            if 'ui_no_automation' in keywords:
                print('去掉ui_no_automation')
                print(id)
                tlc.removeTestCaseKeywords({id: ['ui_no_automation']})
                keywords.remove('ui_no_automation')
        #  API自动化实现的 加上api
        if execution_type == '2':
            if 'api' not in keywords:
                print('加上api')
                print(id)
                keywords.append('api')
                tlc.addTestCaseKeywords({id: keywords})
            if 'api_no_automation' in keywords:
                print('API自动化实现的去掉api_no_automation')
                print(id)
                tlc.removeTestCaseKeywords({id: ['api_no_automation']})
        # 没有api 去掉api_no_automation
        if 'api' not in keywords and 'api_no_automation' in keywords:
            print('没有api的去掉api_no_automation')
            print(id)
            tlc.removeTestCaseKeywords({id: ['api_no_automation']})
