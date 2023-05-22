#!/bin/sh
function check_resource()
{
if [ $# -eq 5 ]
then
    if [ "$1" == "cloudedge-artifacts" ];then
        total=`kubectl get artifacts -n cpaas-system -l chart-purpose=cloudedge,chart-bundle-type=chart-only --no-headers=true|wc -l`
    elif [ "$1" == "cloudedge-helmrequests" ];then
        total=`kubectl get helmrequests -A -l chart-purpose=cloudedge  --no-headers=true|wc -l`
    elif [ "$2" != '' ];then
        total=`kubectl get $1 -n $2  --no-headers=true|wc -l`
    else
        total=`kubectl get $1  --no-headers=true|wc -l`
    fi
    if [[ $total == 0 ]]
    then
        echo "$5 $1 not found"
    else
        if [ "$3" != '' ];then
            if [[ $total -lt $3 ]]
            then
                echo "$5 $1 number is too little $total"
            fi
        fi
        if [ "$4" != '' ];then
            if [ "$2" != '' ];then
                status=`kubectl get $1 -n $2 --no-headers=true|grep -v -P $4|wc -l`
                result=`kubectl get $1 -n $2 --no-headers=true|grep -v -P $4`
            else
                status=`kubectl get $1 --no-headers=true|grep -v -P $4|wc -l`
                result=`kubectl get $1 --no-headers=true|grep -v -P $4`
            fi
            if [ $status -gt 0 ];then
                echo "$5 $1 status error"
                echo $result
            fi
        fi
    fi
else
    echo "请输入五个参数:资源类型 命名空间(集群资源传空字符串) 校验个数(不校验传空字符串 校验传最小值int) 校验状态(不校验传空字符串 校验传状态) 负责人"
fi
}
echo '检查系统组件'
check_resource pod cert-manager '' 'Running|Completed' AIT
check_resource pod cpaas-system '' 'Running|Completed' 所有人
check_resource pod kube-system '' 'Running|Completed' '施源/王珂'
check_resource pod operators '' 'Running|Completed' 赵晓峰
echo '检查准备的数据'
version=`kubectl get cm -n kube-public global-info -o custom-columns=VERSION:.metadata.annotations --no-headers=true|grep -Po 'v3.(\d+)'|grep -Po '(\d+)$'`
check_resource domain '' 10 '' 施源
check_resource virtualmachineimagetemplates '' 3 '' 施源
check_resource chartrepo cpaas-system 5 Synced 赵晓峰
check_resource packagemanifests cpaas-system 20 '' 赵晓峰
if [ $version -ge 10 ];then
check_resource cloudedge-artifacts cpaas-system 1 '' 赵晓峰
check_resource cloudedge-helmrequests '' 1 '' 赵晓峰
fi
if [ $version -ge 12 ];then
check_resource applicationsets argocd 1 '' 赵晓峰
check_resource applications.argoproj.io argocd 1 '' 赵晓峰
fi
