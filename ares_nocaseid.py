# -*- coding:utf-8 -*-
import os
import re
from subprocess import getoutput

import testlink

url = 'http://testlink.alauda.cn/lib/api/xmlrpc/v1/xmlrpc.php'
key = '7ccbcfc2d1c580277d7b5ce1038c9ee6'

tlc = testlink.TestlinkAPIClient(url, key)
test_project_name = os.getenv("PROJECT_TESTLINK", "ACP-master")
test_project_prefix = tlc.getTestProjectByName(test_project_name)['prefix']


def no_caseid():
    # 获取用例不依赖环境，先给token赋一个伪值用来收集用例
    getoutput(f"export TOKEN=testtoken;pytest --collect-only new_case/containerplatform > ./tmp_case")
    result_file = open("./tmp_case", "r")
    results = result_file.readlines()
    # 如果没有获取到测试用例id 就直接退出
    if len(results) == 0:
        print(f"没有获取到自动化测试用例的信息，获取到的结果:{results}")
        exit(1)
    error_case = []
    for result in results:
        try:
            # 只需要对有测试_ 的一行做正则提取
            if "测试" in result:
                # 提取正则两位到六位的数字，现在的caseID基本都在三位数以上了
                if re.findall('_[0-9]{2,6}_', result) == []:
                    error_case.append(result)
        except Exception as e:
            error_case.append(result)
            print(e)

    print(f"没有caseid 如下:{error_case}")
    os.remove("./tmp_case")


if __name__ == "__main__":
    no_caseid()
