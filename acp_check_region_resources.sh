#!/bin/sh
function check_resource()
{
if [ $# -eq 5 ]
then
    if [ "$1" == "certificate" ];then
        total=`kubectl get secret -n cpaas-system -l global-secret=true  --no-headers=true|wc -l`
    elif [ "$1" == "vmimage-credential" ];then
        total=`kubectl get secret -n cpaas-system -l vmimage-credential=true --no-headers=true|wc -l`
    elif [ "$1" == "applications.app.k8s.io" ];then
        total=`kubectl get applications.app.k8s.io -n $2 -l 'sync-from-helmrequest!=true' --no-headers=true|wc -l`
    elif [ "$1" == "applications.app.k8s.io.hr" ];then
        total=`kubectl get applications.app.k8s.io -n $2 -l 'sync-from-helmrequest=true' --no-headers=true|wc -l`
    elif [ "$1" == "frontends" ];then
        total=`kubectl get $1 -n $2 -l 'alb2.cpaas.io/name=ares-alb2' --no-headers=true|wc -l`
    elif [ "$1" == "rules" ];then
        total=`kubectl get $1 -n $2 -l 'alb2.cpaas.io/name=ares-alb2' -l 'alb2.cpaas.io/source-type!=ingress' --no-headers=true|wc -l`
    elif [ "$2" != '' ];then
        total=`kubectl get $1 -n $2 --no-headers=true|wc -l`
    else
        total=`kubectl get $1 --no-headers=true|wc -l`
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
            if [ "$1" == "applications.app.k8s.io" ];then
                status=`kubectl get applications.app.k8s.io -n $2 -l 'sync-from-helmrequest!=true' --no-headers=true|grep -v $4|wc -l`
                result=`kubectl get applications.app.k8s.io -n $2 -l 'sync-from-helmrequest!=true' --no-headers=true|grep -v $4`
            elif [ "$1" == "applications.app.k8s.io.hr" ];then
                status=`kubectl get applications.app.k8s.io -n $2 -l 'sync-from-helmrequest=true' --no-headers=true|grep -v $4|wc -l`
                result=`kubectl get applications.app.k8s.io -n $2 -l 'sync-from-helmrequest=true' --no-headers=true|grep -v $4`
            elif [ "$1" == "topolvmclusters" ];then
                status=`kubectl get $1 -A -o custom-columns=NAME:.metadata.name,STATUS:.status.phase --no-headers=true|grep -v $4|wc -l`
                result=`kubectl get $1 -A -o custom-columns=NAME:.metadata.name,STATUS:.status.phase --no-headers=true|grep -v $4`
            elif [ "$1" == "alaudaloadbalancer2" ];then
                status=`kubectl get $1 -A -o custom-columns=NAME:.metadata.name,STATUS:.status.state --no-headers=true|grep -P 'ares-alb2|ares-port-project'|grep -v $4|wc -l`
                result=`kubectl get $1 -A -o custom-columns=NAME:.metadata.name,STATUS:.status.state --no-headers=true|grep -P 'ares-alb2|ares-port-project'|grep -v $4`
            elif [ "$2" != '' ];then
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
namespace='e2eproject-acp-0-ns'
check_resource applications.core.oam.dev $namespace 25 'running|starting' 史京南
check_resource applications.app.k8s.io $namespace 20 Succeeded 史京南
check_resource applications.app.k8s.io.hr $namespace 1 Succeeded 赵晓峰
check_resource helmrequest $namespace 3 Synced 赵晓峰
check_resource deployment $namespace 50 '(\d+)/\1' 所有人
check_resource daemonset $namespace 2 '(\d+)\s+\1\s+\1\s+\1\s+\1' 郑虎林
check_resource statefulset $namespace 15 '(\d+)/\1' 郑虎林
check_resource cronjob $namespace 20 '' 赵晓峰
check_resource job $namespace 2 '' 赵晓峰
check_resource pod $namespace 50 'Running|Completed' 所有人
check_resource hpa $namespace 1 '' 郑虎林
check_resource cronhpas.tkestack.io $namespace 1 '' 郑虎林
if [ $version -ge 10 ];then
   check_resource vpa $namespace 1 '' 郑虎林
fi
check_resource configmap $namespace 40 '' 郑虎林
check_resource secret $namespace 25 '' 郑虎林
check_resource service $namespace 45 '' 施源
check_resource ingress $namespace 10 '' 施源
if [ $version -ge 9 ];then
check_resource gateways $namespace 3 '' 王珂
check_resource httproutes $namespace 70 '' 王珂
fi
check_resource pvc $namespace 10 Bound 刘明宇
if [ $version -ge 8 ];then
check_resource alaudabucketrequests $namespace 1 '' 刘明宇
fi
check_resource frontends cpaas-system 20 '' 王珂
check_resource rules cpaas-system 15 '' 王珂

check_resource crd '' 200 '' 郑虎林
check_resource certificate '' 10 '' 施源
if [ $version -ge 10 ];then
check_resource ipaddresspools metallb-system 3 '' 王珂
check_resource pod metallb-system '' 'Running|Completed' 王珂
fi
check_resource subnets '' 5 '' '施源/王珂'
underlay_flag=`kubectl get subnet ovn-default -o custom-columns=NAME:.metadata.name,VLAN:.spec.vlan --ignore-not-found=true --no-headers=true|grep -v none|wc -l`
if [ $underlay_flag == 1 ];then
check_resource provider-networks '' 2 '' 王珂
check_resource vlans '' 2 '' 王珂
check_resource deployment e2eproject-acp-0-ns-u1 1 '(\d+)/\1' 王珂

fi
ovn_flag=`kubectl get subnet ovn-default --ignore-not-found=true --no-headers=true|wc -l`
if [ $ovn_flag == 1 ];then
check_resource deployment e2eproject-acp-0-ns-ovn1 2 '(\d+)/\1' 王珂
check_resource deployment e2eproject-acp-0-ns-ovn8 9 '(\d+)/\1' 王珂
check_resource daemonset e2eproject-acp-0-ns-ovn8 9 '(\d+)\s+\1\s+\1\s+\1\s+\1' 王珂
check_resource daemonset e2eproject-acp-0-ns-ovn9 1 '(\d+)\s+\1\s+\1\s+\1\s+\1' 王珂
check_resource statefulset e2eproject-acp-0-ns-ovn8 9 '(\d+)/\1' 王珂
check_resource networkpolicy e2eproject-acp-0-nwp-0 10 '' 王珂
fi
calico_flag=`kubectl get subnet default-ipv4-ippool --ignore-not-found=true --no-headers=true|wc -l`
if [ $calico_flag == 1 ];then
check_resource deployment e2eproject-acp-0-ns-calicoa 1 '(\d+)/\1' 施源
check_resource deployment e2eproject-acp-0-ns-calicob 1 '(\d+)/\1' 施源
check_resource deployment e2eproject-acp-0-ns-calicoc 1 '(\d+)/\1' 施源
if [ $version -ge 11 ];then
check_resource deployment e2eproject-acp-0-ns-vxlan-calicoa 1 '(\d+)/\1' 施源
check_resource deployment e2eproject-acp-ns-vxlan-calicob 1 '(\d+)/\1' 施源
fi
check_resource networkpolicy e2eproject-acp-0-nwp-0 10 '' 施源
fi
check_resource alaudaloadbalancer2 cpaas-system 3 ready 王珂
check_resource tracejobs '' 10 '' 王珂
check_resource tracejobreports '' 4 '' 王珂
check_resource storageclasses '' 10 '' 刘明宇
check_resource persistentvolumes '' 40 '' 刘明宇
check_resource storageclasses '' 5 '' 刘明宇
check_resource volumesnapshots $namespace 1 '' 刘明宇
check_resource cephclusters rook-ceph 1 HEALTH_OK 刘明宇
check_resource pod rook-ceph '' 'Running|Completed' 刘明宇
check_resource cephfilesystems rook-ceph 1 Ready 刘明宇
check_resource cephblockpools rook-ceph 1 '' 刘明宇
check_resource cephobjectstores rook-ceph 1 '' 刘明宇
check_resource topolvmclusters nativestor-system 1 Ready 刘明宇
check_resource pod nativestor-system '' 'Running|Completed' 刘明宇
if [ $version -ge 8 ];then
check_resource buckets '' 1 '' 刘明宇
fi
check_resource vmimage-credential cpaas-system 1 '' 施源
check_resource clusterserviceversions operators 10 '' 赵晓峰
node=`kubectl get node --no-headers=true|grep -v master|wc -l`
if [ $node -gt 0 ];then
check_resource nodegroups '' 1 Active 史京南
check_resource deployment e2eproject-acp-1-ns 2 '(\d+)/\1' 史京南
fi
check_resource deployment e2eproject-acp-1-ns 1 '(\d+)/\1' 史京南