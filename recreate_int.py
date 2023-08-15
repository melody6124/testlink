import base64
import json
from random import choice
from time import sleep
from urllib.parse import urlparse, parse_qsl

import requests
import rsa
import urllib3
from bs4 import BeautifulSoup
from jira import JIRA

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

virt_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImQ5YzEyNDljN2FhNzIwOGYzNGJjNGY5NzQzZDIzZmY0ZjNmMDAwZWEiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiI4MDZmNGY5MC1iNjk5LTQxNTgtYjNmYy1lOGY1Mjk1ZWZmM2IiLCJpYXQiOjE2OTAzNTI1MTgsInR5cCI6IkFjY2Vzc1Rva2VuIiwiZW1haWwiOiJqbnNoaUBhbGF1ZGEuaW8ifQ.Xmjm45lzKua5HBr2VXRLXtI2mvlkv1TUkKEMff28zhPrA2vrtXOtOtTmOw2WPvC4mhLRpf9bfT55gFGWDmVngq40sVZ4V-u9pcsd68Tze1ZMEXH6HhJc_mjHSTddWjHAIi6K8yIy_GXINAVSPDcKNNDQnndCQwsHOKmOyEIyqzotxO2W9Y-oeAeq0d4CL_FJwpIsdIFT8uIklzl2zxtCPbtIZHU1dNZL8dhNzB4NVXNyDQOq-Qm5Vz7poIq2_kZz7aF8kvUa0f6cNpyHacQ-UpkrD1q_yPl11qn-iosmZr6Nxtui0-mrz2lUdx-pvU67m4idxquiZq1svWl3-Enb2w"


def get_vm(keyword):
    vm_url = f"https://virt-global.alauda.cn/acp/v1/resources/search/kubernetes/physical/apis/kubevirt.io/v1/namespaces/test-qa/virtualmachines?limit=20&keyword={keyword}&field=metadata.name"
    vm_ret = requests.get(vm_url, headers={'Authorization': f"Bearer {virt_token}"}, verify=False)
    vm_name_list = []
    for item in vm_ret.json()['items']:
        vm_name_list.append(item['metadata']['name'])
    return vm_name_list


def delete_vm(keyword):
    # 删除旧的机器
    vm_name_list = get_vm(keyword)
    print(vm_name_list)
    if 7 <= len(vm_name_list) <= 10:
        batch_delete_data = {
            "apiVersion": "batch.alauda.io/v1alpha1",
            "kind": "BatchAction",
            "metadata": {
                "generateName": "batch-vm-delete-",
                "namespace": "test-qa"
            },
            "spec": {
                "actions": [
                    {
                        "name": "delete",
                        "verb": "delete",
                        "target": {
                            "names": vm_name_list,
                            "resource": {
                                "group": "kubevirt.io",
                                "version": "v1alpha3",
                                "resource": "virtualmachines"
                            }
                        }
                    }
                ]
            }
        }
        print(batch_delete_data)
        batch_delete_url = "https://virt-global.alauda.cn/kubernetes/physical/apis/batch.alauda.io/v1alpha1/namespaces/test-qa/batchactions"
        delete_ret = requests.post(batch_delete_url, json=batch_delete_data, headers={'Authorization': f"Bearer {virt_token}"}, verify=False)
        print(delete_ret.status_code)
        print(delete_ret.text)


def auto_deploy(package, keyword, region):
    # 查看配额是否满足，满足后触发流水线部署
    nsoverviews_url = "https://virt-global.alauda.cn/acp/v1/kubernetes/physical/namespaceoverviews/test-qa/resourcequota"
    overview_ret = requests.get(nsoverviews_url, headers={'Authorization': f"Bearer {virt_token}"}, verify=False)
    if 'm' not in overview_ret.json()['used']['limits.cpu']:
        free_cpu = int(overview_ret.json()['hard']['limits.cpu']) - int(overview_ret.json()['used']['limits.cpu'])
    else:
        free_cpu = int(overview_ret.json()['hard']['limits.cpu']) - int(overview_ret.json()['used']['limits.cpu'].rstrip('m')) / 1024
    print(free_cpu)
    free_memory = int(overview_ret.json()['hard']['limits.memory'].rstrip('Gi')) - int(overview_ret.json()['used']['limits.memory']) / 1024 / 1024 / 1024
    print(free_memory)
    free_storage = int(overview_ret.json()['hard']['requests.storage'].rstrip('Gi')) - int(overview_ret.json()['used']['requests.storage'].rstrip('Gi'))
    print(free_storage)
    if free_cpu >= 68 and free_memory >= 136 and free_storage >= 1140:
        # 流水线部署
        # https://confluence.alauda.cn/pages/viewpage.action?pageId=149589969
        deploy_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjMzMTA2NTg2MDZlNGFmOTZhOGQwMDQwZTFlYjYyNTE4ZTdlZGQ5YTYiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiI5NjU3ZTAwNi0zMzIxLTQ0NzAtOTgyMi1iMTc0MWYwN2Y0ZjUiLCJpYXQiOjE2OTAzNTY1NjgsInR5cCI6IkFjY2Vzc1Rva2VuIiwiZW1haWwiOiJqbnNoaUBhbGF1ZGEuaW8ifQ.gDK-1KQ8M1lc2WvXtj7g4f4Oglp856EPxEhhj5KZ5MCNcRgsPzfYNHI2GJyKCYyhP7NTUcTlTgDqDazap8pDEuauv7gBxFg7FGNAzVmr5ef-MTWYrvYOGlTvZO1PxkRAZ5z--hog4l_ZcYnp4KzLBmJHNl8l1Ur9jQGqsoonCEty_LS_CoglBiHTlCle3kTeRYVsQSCAOAOSTsbdbCbDHaCk7c02nKh9bLRABLGIUChDUSyr2EFiEAZOCpRLsl0SR8lPWinwUEExgNidCV_UbadYRnOYneeu0KclLupPqWVgSOKiLshag6KVw2hXUFmxGbWkGDBX6WM8CbCuJMhvPQ"
        deploy_url = "https://build.alauda.cn/devops/api/v1/pipelineconfig/ops/auto-deploy/trigger"
        os_list = ['c79', 'c78', 'c77', 'c76', 'u2204', 'u2004', 'r86', 'r80', 'r78', 'kylinv10', 'kylinv10sp1', 'kylinv10sp2']
        os = choice(os_list)
        print(os)
        deploy_data = {"params": [
            {"name": "PACKAGER_DOWNLOAD_URL", "type": "StringParameterDefinition", "value": package,
             "show": None, "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "OVN_REGION", "type": "BooleanParameterDefinition", "value": "", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "CALICO_REGION", "type": "BooleanParameterDefinition", "value": "", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "OTHER_REGION", "type": "StringParameterDefinition", "value": region, "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "GLOBAL_COUNT", "type": "StringParameterDefinition", "value": "1", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "OTHER_PARAMETERS", "type": "StringParameterDefinition", "value": "", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "OS", "type": "StringParameterDefinition", "value": os, "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "OVN_REGION_NODE_COUNT", "type": "StringParameterDefinition", "value": "0", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "PLATFORM_DOMAIN_NAME", "type": "StringParameterDefinition", "value": "", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "GLOBAL_HA", "type": "BooleanParameterDefinition", "value": "", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "PROJECT_NAME", "type": "StringParameterDefinition", "value": keyword, "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "ASSESS_REGISTRY", "type": "BooleanParameterDefinition", "value": "true", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "DONOT_DELETE", "type": "BooleanParameterDefinition", "value": "true", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "CASE_TYPE_AND_PATH", "type": "StringParameterDefinition", "value": "DoNotTest", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "CALICO_REGION_NODE_COUNT", "type": "StringParameterDefinition", "value": "0", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "GLOBAL_TYPE", "type": "StringParameterDefinition", "value": "101", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "WAITRSYNCPACKAGE", "type": "BooleanParameterDefinition", "value": "", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "CALICO_REGION_HA", "type": "BooleanParameterDefinition", "value": "", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}},
            {"name": "OVN_REGION_HA", "type": "BooleanParameterDefinition", "value": "", "show": None,
             "display": {"type": "", "name": {}, "argument": {"relatedFiled": "", "values": None}}}]}
        deploy_ret = requests.post(deploy_url, json=deploy_data, headers={'Authorization': f"Bearer {deploy_token}"}, verify=False)
        print(deploy_ret.status_code)
        print(deploy_ret.text)
        print(f"https://build.alauda.cn/console-devops/workspace/ops/pipelines/all/auto-deploy/{deploy_ret.json()['metadata']['name']}?isMultiBranch=0")
        print(f"https://virt-global.alauda.cn/console-acp/workspace/test~physical~test-qa/virtual-machine/list?keyword={keyword}")
    else:
        print("资源不足")


def get_package():
    # 获取pass对应的online包
    ret = requests.get("http://192.168.144.3:12345/IDC/")
    report = BeautifulSoup(ret.text, "html.parser")
    installer = ""
    pass_list = []
    for name in report.a.next_siblings:
        if "href" in str(name) and "-pass" in name.text:
            installer = name.text.split('-alpha.')[0]
            pass_list.append(name.text.split('-alpha.')[1].split('-')[0])
    package = f"http://192.168.144.3:12345/IDC/{installer}-alpha.{max(pass_list)}-online.tar"
    return package


def get_token(API_URL, idp_name="local", username="admin", password="07Apples@"):
    url = API_URL + "/console-platform/api/v1/token/login"
    r = requests.get(url, verify=False, timeout=15)
    auth_url = r.json()["auth_url"]
    params = {
        "access_type": dict(parse_qsl(urlparse(auth_url).query)).get("access_type"),
        "client_id": dict(parse_qsl(urlparse(auth_url).query)).get("client_id"),
        "nonce": dict(parse_qsl(urlparse(auth_url).query)).get("nonce"),
        "redirect_uri": f"{API_URL}/console-platform",
        "response_type": dict(parse_qsl(urlparse(auth_url).query)).get("response_type"),
        "scope": dict(parse_qsl(urlparse(auth_url).query)).get("scope"),
        "state": dict(parse_qsl(urlparse(auth_url).query)).get("state"),
    }
    auth_url = "{}/dex/api/v1/authorize".format(API_URL)
    r = requests.get(auth_url, verify=False, params=params)
    req = r.json()["req"]
    url = "{}/dex/api/v1/authorize/{}?req={}".format(API_URL, idp_name, req)
    # generate connectorID
    requests.get(url, verify=False, timeout=10)
    ret = requests.get("{}/dex/pubkey".format(API_URL), verify=False)
    content = ret.json()
    ts_num = content.get("ts")
    pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(content.get("pubkey"))
    data = {"ts": ts_num, "password": password}
    crypto = rsa.encrypt(json.dumps(data).encode("utf8"), pub_key)
    pwd = str(base64.b64encode(crypto), "utf8")
    data = {"account": str(username), "password": pwd}
    response = requests.post(url, json=data, verify=False, timeout=10)
    assert response.status_code == 200, f"登陆失败:{response.text}"
    redirect_url = response.json()["redirect_url"]
    code = dict(parse_qsl(urlparse(redirect_url).query)).get("code")
    state = dict(parse_qsl(urlparse(redirect_url).query)).get("state")
    url = f"{API_URL}/console-platform/api/v1/token/callback"
    params = {"code": code, "state": state}
    r = requests.get(url, verify=False, params=params)
    ret = r.json()
    token_type = ret["token_type"]
    access_token = ret["access_token"]
    # 不会过期的token
    forver_auth = "{} {}".format(token_type.capitalize(), access_token)
    return forver_auth


def jira_comment(keyword, jira, package):
    # jira 添加comment 环境信息
    vmi_url = f"https://virt-global.alauda.cn/acp/v1/resources/search/kubernetes/physical/apis/kubevirt.io/v1/namespaces/test-qa/virtualmachineinstances?limit=20&keyword={keyword}&field=metadata.name"
    vmi_ret = requests.get(vmi_url, headers={'Authorization': f"Bearer {virt_token}"}, verify=False)
    vmi_list = {}
    for item in vmi_ret.json()['items']:
        vmi_list.update({item['metadata']['name']: item['status']['interfaces'][0]['ipAddress']})
    vm_url = f"https://virt-global.alauda.cn/acp/v1/resources/search/kubernetes/physical/apis/kubevirt.io/v1/namespaces/test-qa/virtualmachines?limit=20&keyword={keyword}-m-1&field=metadata.name"
    vm_ret = requests.get(vm_url, headers={'Authorization': f"Bearer {virt_token}"}, verify=False)
    os = vm_ret.json()['items'][0]['metadata']['labels']['virtualization.cpaas.io/image-name']
    for key, value in vmi_list.items():
        if f'{keyword}-m-1' in key:
            ip = value
            break
    comment = f"API_URL=https://{ip}\nUSERNAME=admin\nPASSWORD=07Apples@\nOS={os}\nPACKAGE={package}\nVM_INFO={vmi_list}"
    print(comment)
    jiras = JIRA(server="https://jira.alauda.cn", basic_auth=("jnshi", "1021nanjing.?"))
    jiras.add_comment(jira, comment)
    # 更新许可证
    API_URL = f'https://{ip}'
    token = get_token(API_URL)
    url = f"{API_URL}/lic/v2/licenses?limit=20&kind=license"
    list_ret = requests.get(url, headers={'Authorization': f"{token}"}, verify=False)
    print(list_ret.status_code)
    name = list_ret.json()['items'][0]['metadata']['name']
    delete_url = f"{API_URL}/lic/v2/licenses/{name}"
    del_ret = requests.delete(delete_url, headers={'Authorization': f"{token}"}, verify=False)
    print(del_ret.status_code)
    url = f"{API_URL}/acp/v2/resources/global/resources"
    payload = [{"apiVersion": "operator.alauda.io/v1alpha1", "kind": "ResourcePatch",
                "metadata": {"labels": {"target": "c794a6553803fdbf45633a567ea9388a"}, "name": "change-demo-days"},
                "spec": {"jsonPatch": [{"op": "add", "path": "/spec/template/spec/containers/0/env/4", "value": {"name": "DEMO_DAYS", "value": "90"}}],
                         "release": "cpaas-system/alauda-base",
                         "target": {"apiVersion": "apps/v1", "kind": "Deployment", "name": "archon", "namespace": "cpaas-system"}}}]

    license_ret = requests.post(url, json=payload, headers={'Authorization': f"{token}"}, verify=False)
    print(license_ret.status_code)
    # 更新日志存储组件
    url = f"{API_URL}/kubernetes/global/apis/cluster.alauda.io/v1alpha1/moduleinfoes?limit=0&labelSelector=cpaas.io/module-type=plugin,cpaas.io/cluster-name=global,cpaas.io/module-name=logcenter"
    ret = requests.get(url, headers={'Authorization': f"{token}"}, verify=False)
    if len(ret.json()['items']) == 1:
        mid = ret.json()['items'][0]['metadata']['name']
        url = f"{API_URL}/apis/cluster.alauda.io/v1alpha1/moduleinfoes/{mid}"
        data = {
            "spec": {
                "config": {
                    "ttl": {
                        "audit": 1, "event": 1, "logKubernetes": 1, "logPlatform": 1, "logSystem": 1, "logWorkload": 1
                    }
                }
            }
        }
        ret = requests.patch(url, json=data, headers={'Authorization': f"{token}", 'Content-Type': "application/merge-patch+json"}, verify=False)
        print(ret.status_code)


if __name__ == "__main__":
    keyword = "qa-acp-int"
    jira_id = "SERVER-1978"
    # region = "ca,c,m1r1,SA2,DS50,DSA5#ovn,o,m1r3,SA2,DS50,DSA50"
    # delete_vm(keyword)
    # sleep(60)
    # package = get_package()
    # print(package)
    package = "http://192.168.144.3:12345/IDC/installer-v3.14.0-alpha.297-online.tar"
    # auto_deploy(package, keyword, region)
    # print("环境部署中，等待一个半小时，请勿关闭")
    # sleep(60 * 90)
    jira_comment(keyword, jira_id, package)
