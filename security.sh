#!/bin/bash
CMD_NAME=$0
function usage() {
    echo "
${CMD_NAME} <$1>
ARGS:
1     "全网监听"
2     "嗅探工具"
3     "解密或破解工具二进制检查"
4     "解密或破解文件检查"
5     "进程非root检查"
6     "容器非root检查"
7     "特权容器 privileged 检查"
8     "特权容器 capabilities 检查"
9     "宿主机明文传输检查"
10    "容器明文传输"
11    "高危端口检查"
12    "sudoers 特权检查"
13    "env 敏感信息检查"
14    "普通用户UID为特权用户组检查"
15    "普通用户可login检查"
"
}

function coler() {
           case $1 in
      black)
           echo -e "\033[40;37m $2 \033[0m" >&2
            ;;
        red)
           echo -e "\033[41;37m $2 \033[0m" >&2
            ;;
      green)
           echo -e "\033[42;37m $2 \033[0m" >&2
            ;;
      yello)
           echo -e "\033[43;37m $2 \033[0m" >&2
           ;;
      blue)
           echo -e "\033[44;37m $2 \033[0m" >&2
           ;;
      purple)
           echo -e "\033[45;37m $2 \033[0m" >&2
           ;;
      blue2)
           echo -e "\033[46;37m $2 \033[0m" >&2
           ;;
        white)
           echo -e "\033[47;30m $2 \033[0m" >&2
           ;;
          *)
          esac
}

function if_tools() {
    if [ $(command -v jq >/dev/null 2>&1;echo $?) -ne 0 ]; then
      echo '机器上没有jq命令' >&2
      export PATH="$PATH:/tmp"
    fi
}

function get_cri() {
    if [ $(command -v docker >/dev/null 2>&1;echo $?) -eq 0 ]; then
        echo "docker"
    else
        echo "containerd"
    fi
}

function 01_net_listen() {
   local white_list=(111 68 22)
   local  ret=`netstat -lntup|awk '{print $4,$NF}'|egrep "0.0.0.0|:::" |awk '{print $1}'|awk -F: '{print $NF}'|sort |uniq`
   for white in "${white_list[@]}";do
       local ret=`echo -e "${ret}"|grep -v "${white}"`
   done
   local tmp_ret=""
   for port in $(echo -e "${ret}");do
       local pid=$(netstat -ntpl |grep ":${port} " |grep -v 'grep' |awk -F 'LISTEN' '{print $NF}'|awk '{print $1}' |awk -F '/' '{print $1}' |sort -u)
       if [ "${pid}" == "" ];then
#           echo "No process information was found for the port [${listen_port}]。" >&2
           continue
       else
           local process_info=$(ps -ax --format pid,command |grep "^ *${pid} " |grep -v 'grep')
       fi
       local tmp_ret="${tmp_ret}${port} || ${process_info}\n"
   done
   local ret=$(echo -e "${ret}" |sed '/^$/d')
   if [ "${ret}" != "" ];then
       echo -e "$tmp_ret"
       exit 1
   fi
}

function 02_sniffing_tool() {
    # shellcheck disable=SC2140
    if_tools
    local ret=""
    TOOLS="-iname tcpdump -o -iname "sniffer" -o -iname "wireshark" -o -iname "netcat" -o -iname "gdb" -o -iname "strace" -o -iname "readelf" -o -iname "cpp" -o -iname "gcc" -o -iname "dexdump" -o -iname "mirror" -o -iname "JDK" -o -iname "nc" "
    if [ "$(get_cri)" == "docker" ];then
        for i in $(find /var/lib/docker/overlay2/ $TOOLS|grep bin)
            do
            volum_id=$(echo $i|awk -F/ '{print $6}')
            container_name=$(docker inspect $(docker ps -qa) | jq -r 'map([.Name, .GraphDriver.Data.MergedDir]) | .[] | "\(.[0])\t\(.[1])"'|grep $volum_id|awk '{print $1}')
            file_path=$(echo $i|awk -F$volum_id '{print $NF}')
            [[ $container_name != '' ]]&& local ret="${ret}${file_path} ${container_name}\n"
        done
    else
        for i in $(find /run/containerd/io.containerd.runtime.v2.task/k8s.io/ $TOOLS|grep bin)
          do
          volum_id=$(echo $i|awk -F/ '{print $6}')
          volum_id_short=$(echo $i|awk -F/ '{print $6}'|cut -b 1-13)
          container_name=$(crictl inspect "${volum_id_short}" |jq -r '["", .status.labels["io.kubernetes.container.name"], .status.labels["io.kubernetes.pod.name"], .status.labels["io.kubernetes.pod.namespace"], ""] | join("_")')
          file_path=$(echo $i|awk -F$volum_id '{print $NF}')
          if [[ -n "${container_name}" ]];then
              local ret="${ret}${file_path} ${container_name}\n"
          else
              continue
          fi
        done
    fi
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 03_sensitive_tool_binary() {
    if_tools
    local ret=""
    local TOOLS=" -iname "*hydra*" -o -iname "*cain-abel*" -o -iname "*patator*" -o -iname "*webbruteforce*" -o -iname "*ripper*"  -o -iname "*lumberjack*"  -o -iname "*teenet*" -o -iname "*vncrack*""
    for i in $(find /var/lib/docker/overlay2/ $TOOLS)
        do
        if [ -f $i ];then
            volum_id=$(echo $i|awk -F/ '{print $6}')
            container_name=$(docker inspect $(docker ps -qa) | jq -r 'map([.Name, .GraphDriver.Data.MergedDir]) | .[] | "\(.[0])\t\(.[1])"'|grep $volum_id|awk '{print $1}')
            file_path=$(echo $i|awk -F$volum_id '{print $NF}')
            [[ $container_name != '' ]]&& local ret="${ret}${file_path} ${container_name}\n"
        fi
    done
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 04_sensitive_tool_file() {
    if_tools
    local ret=""
    for i in $(find /var/lib/docker/overlay2/ -type f -iname "*.sh" | xargs grep "decrypt|passwd")
        do
        if [ -f $i ];then
           local volum_id=$(echo $i|awk -F/ '{print $6}')
           local container_name=$(docker inspect $(docker ps -qa) | jq -r 'map([.Name, .GraphDriver.Data.MergedDir]) | .[] | "\(.[0])\t\(.[1])"'|grep $volum_id|awk '{print $1}')
           local file_path=$(echo $i|awk -F$volum_id '{print $NF}')
           [[ $container_name != '' ]]&& local ret="${ret}${file_path} ${container_name}\n"
       fi
    done
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 05_process_root_check() {
    local ret=""
    if [[ $EUID -ne 0 ]]; then
       echo "This script must be run as root"
       exit 1
    fi
    if [ "$(get_cri)" == "docker" ];then
        for dockerid in $(docker ps -f label=io.kubernetes.docker.type=container |grep -v "CONTAINER ID"|awk '{print $1}')
            do
            local POD_NAME=$(docker ps |grep $dockerid |awk '{print $NF}')
            local PID=$(docker inspect $dockerid --format '{{.State.Pid}}')
            if [ "$(ps -ef|grep $PID |awk '{if ($1 == "root" && $2 == '"$PID"')print "'$POD_NAME'" }')" != "" ];then
                local ret="${ret}$(ps -ef|grep $PID |awk '{if ($1 == "root" && $2 == '"$PID"')print "'$POD_NAME'" }')\n"
            fi
        done
    else
        for container in $(crictl ps  --output json | jq -r '.containers[].id'|cut -b 1-13); do
            container_name=$(crictl inspect "${container}" |jq -r '["", .status.labels["io.kubernetes.container.name"], .status.labels["io.kubernetes.pod.name"], .status.labels["io.kubernetes.pod.namespace"], ""] | join("_")')
            if [ $(crictl inspect $container | jq -r '.info.runtimeSpec.process.user.uid') -eq 0 ]; then
                local ret="${ret}${container_name}\n"
            fi
        done
    fi
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 06_container_root_check() {
    local ret=""
    for con in $(docker ps -f label=io.kubernetes.docker.type=container |egrep -v "CONTAINER|pause" |awk '{print $1}')
        do
        docker exec -it $con id |grep "uid=0" >/dev/null 2>&1
        [ $? -eq 0 ]&& image=$(docker ps |grep $con |awk '{print $NF}')
        local ret="${ret}$image\n"
    done
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 07_privileged() {
    if_tools
    local ret=""
    if [ "$(get_cri)" == "docker" ];then
        for i in $(docker ps --quiet | sort| xargs docker inspect --format '{{.Id}}:Privileged={{.HostConfig.Privileged }}'|grep true 2>/dev/null|awk -F: '{print $1}'|cut -c 1-6)
            do
            if [ ! "`docker ps -a|grep $i |grep -v k8s_POD`" == "" ];then
                local ret="${ret}`docker ps -a|grep $i|awk '{print $NF}'`\n"
            fi
        done
    else
        if [[ $EUID -ne 0 ]]; then
           echo "必须以 root 运行脚本"
           exit 2
        fi
        for container in $(crictl ps  --output json | jq -r '.containers[].id'|cut -b 1-13); do
            container_name=$(crictl ps |grep $container|awk '{print $7}')
            if crictl inspect "${container}" | grep -q '"privileged": true'; then
                container_name=$(crictl inspect "${container}" |jq -r '["", .status.labels["io.kubernetes.container.name"], .status.labels["io.kubernetes.pod.name"], .status.labels["io.kubernetes.pod.namespace"], ""] | join("_")')
                local ret="${ret}${container_name}\n"
            fi
        done
    fi
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 08_capabilities() {
    local ret=""
    for i in $(docker ps --quiet| sort| xargs docker inspect --format '{{.Id}}  :  CapAdd={{.HostConfig.CapAdd }}'|grep -v "no value"|awk -F: '{print $1}'|cut -c 1-6)
      do
      local ret="${ret}`docker ps -a|grep $i|awk '{print $NF}'`\n"
    done
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}


function 09_plaintext_transmission() {
    local ret=""
    # 负载安全的运维同事同意加的白名单，alb http端口默认忽略
    local white_list=(22 68 111 11780 9080 11782 9099 9404 1936 6060 53 80 20257)
    for port in $(netstat -lntup|egrep -v "Proto|127.0.0.1|Active"|awk '{print $4}')
    do
      ip_port_addr=$port
      ip_address=$(ifconfig |grep 192.168|awk '{print $2}')
      listen_port=$(echo $port|awk -F: '{print $NF }')
      echo $port|egrep ':::|0.0.0.0' >/dev/null 2>&1
      if [ $? -eq 0 ];then
         ip_port_addr=$ip_address:$listen_port
         echo Q | timeout 1 openssl s_client -connect $ip_port_addr 2>&1|grep -v "error:140770FC:SS"|grep "CERTIFICATE" >>/dev/null
         if [[ $? -ne 0 ]] && [[ ! "${white_list[*]}" =~ ${listen_port} ]];then
            local pid=$(netstat -ntpl |grep ":${listen_port} " |grep -v 'grep' |awk -F 'LISTEN' '{print $NF}'|awk '{print $1}' |awk -F '/' '{print $1}' |sort -u)
            if [ "${pid}" == "" ];then
#                echo "No process information was found for the port [${listen_port}]。" >&2
                continue
            else
                local process_info=$(ps -ax --format pid,command |grep "^ *${pid} " |grep -v 'grep')
            fi

            local ret="${ret}${listen_port} || ${process_info}\n"
         fi
      fi
    done
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"|sort|uniq
        exit 1
    fi
}


function 10_container_plaintext_transmission() {
    local ret=""
    for ep_add in $(kubectl get ep -A|awk '{print $2"_"$3}'|egrep -v "192|ENDPOINTS")
        do
        local address=$(echo $ep_add|awk -F_ '{print $2}')
        local service=$(echo $ep_add|awk -F_ '{print $1}')
        for ip_addr in  $address
          do
            OLD_IFS="$IFS"
            IFS=", "
            echo Q | timeout 1 openssl s_client -connect  $ip_addr  2>&1|grep "CERTIFICATE" >/dev/null
            if [ $? -ne 0 ];then
               local ret="${ret}${ip_addr},${service}\n"
            fi
        done
    done
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 11_critical_port() {
    local ret=""
    local ports=(20 21 23 69 135 137 138 139 177 389 445 513 1433 1434 1435 1521 1522 1523 1524 1525 1526 1527 1528 1529 1530 3389 4899 8888 3306 6000 6001 6002 6003 6004 6005 6006 6007 6008 6009 6010 6011 6012 6013 6014 6015 6016 6017 6018 6019 6020 6021 6022 6023 6024 6025 6026 6027 6028 6029 6030 6031 6032 6033 6034 6035 6036 6037 6038 6039 6040 6041 6042 6043 6044 6045 6046 6047 6048 6049 6050 6051 6052 6053 6054 6055 6056 6057 6058 6059 6060 6061 6062 6063 50000 50001 50002 50003 50004 50005 50006 50007 50008 50009 50010 50011 50012 50013 50014 50015 50016 50017 50018 50019 50020 50021 50022 50023 50024 50025 50026 50027 50028 50029 50030 50031 50032 50033 50034 50035 50036 50037 50038 50039 50040 50041 50042 50043 50044 50045 50046 50047 50048 50049 50050)
    for listen in $(netstat -lntup|egrep -v "Active|Proto" |awk '{print $4}'|awk -F: '{print $NF}' |sort -u)
        do
        for port in ${ports[*]};do
            if [[ "${port}" == "${listen}" ]];then
                local pid=$(netstat -ntpl |grep ":${listen} " |grep -v 'grep' |awk -F 'LISTEN' '{print $NF}'|awk '{print $1}' |awk -F '/' '{print $1}' |sort -u)
                if [ "${pid}" == "" ];then
#                    echo "No process information was found for the port [${listen_port}]。" >&2
                    continue
                else
                    local process_info=$(ps -ax --format pid,command |grep "^ *${pid} " |grep -v 'grep')
                fi

                local ret="${ret}${listen} || ${process_info}\n"
            fi
        done
    done
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 12_sudoers_check() {
    coler green  "检查是否支持sudo"
    if_tools
    local ret=""
    if [ "$(get_cri)" == "docker" ];then
        for i in $(find /var/lib/docker/overlay2/ -type f -name sudoers | grep "/etc/sudoers")
            do
            if [ -f $i ];then
                grep "ALL=(ALL)" $i >/dev/null 2>&1
                    if [ $? -eq 0 ];then
                        local volum_id=$(echo $i|awk -F/ '{print $6}')
                        local container_name=$(docker inspect $(docker ps -qa) | jq -r 'map([.Name, .GraphDriver.Data.MergedDir]) | .[] | "\(.[0])\t\(.[1])"'|grep $volum_id|awk '{print $1}')
                        local file_path=$(echo $i|awk -F$volum_id '{print $NF}')
                        [[ -n "${container_name}" ]]&&  local ret="${ret}\n${file_path} || ${container_name}"
                    fi
              fi
        done
    else
        for i in $(find /run/containerd/io.containerd.runtime.v2.task/k8s.io/ -type f -name sudoers | grep "/etc/sudoers")
             do
             volum_id=$(echo $i|awk -F/ '{print $6}')
             volum_id_short=$(echo $i|awk -F/ '{print $6}'|cut -b 1-13)
             file_path=$(echo $i|awk -F$volum_id '{print $NF}')
             container_name=$(crictl inspect "${volum_id_short}" |jq -r '["", .status.labels["io.kubernetes.container.name"], .status.labels["io.kubernetes.pod.name"], .status.labels["io.kubernetes.pod.namespace"], ""] | join("_")')
             if [ -f $i ];then
                 grep "ALL=(ALL)" $i 1>&2
                 if [ $? -eq 0 ];then
                    [[ -n "${container_name}" ]]&& local ret="${ret}\n${file_path} || ${container_name}"
                 fi
             fi
        done
    fi
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 13_check_env() {
    coler green  "检查容器环境变量是否含敏感信息"
    if_tools
    local ret=""
    for dockerid in `docker ps -f label=io.kubernetes.docker.type=container|grep -v "CONTAINER ID"|awk '{print $1}' `
        do
        local POD_NAME=$(docker ps |grep $dockerid |awk '{print $NF}')
        export POD_NAME
        local PID=$(docker inspect $dockerid |jq -r '.[0].Config.Env[]')
        for env in $PID
            do
            local env_key=$(echo "${env}"|awk -F '=' '{print $1}')
            local ret="${ret}\n`echo "${env_key} || ${POD_NAME}"|egrep "PASSWORD|password|TOKEN|token"`"
        done
    done
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 14_check_uid() {
    coler green  "检查用户的uid，不允许普通用户uid为0"
    local ret=""
    if_tools
    if [ "$(get_cri)" == "docker" ];then
    for i in $(find /var/lib/docker/overlay2/ -name passwd|grep "/etc/passwd")
        do
        if [ -f $i ];then
            local volum_id=$(echo $i|awk -F/ '{print $6}')
            local container_name=$(docker inspect $(docker ps -qa) | jq -r 'map([.Name, .GraphDriver.Data.MergedDir]) | .[] | "\(.[0])\t\(.[1])"'|grep $volum_id|awk '{print $1}')
            local file_path=$(echo $i|awk -F$volum_id '{print $NF}')
            if [ -n "${container_name}" ];then
                local ret="${ret}\n`cat $i |grep -v root|awk -F: '{if ($4 == 0) print $1 " || '$container_name'"}'`"
            fi
        fi
    done
    else
        for i in $(find /run/containerd/io.containerd.runtime.v2.task/k8s.io/ -name passwd|grep "/etc/passwd")
            do
            if [ -f $i ];then
                volum_id=$(echo $i|awk -F/ '{print $6}'|cut -b 1-13 )
                container_name=$(crictl inspect "${volum_id}" |jq -r '["", .status.labels["io.kubernetes.container.name"], .status.labels["io.kubernetes.pod.name"], .status.labels["io.kubernetes.pod.namespace"], ""] | join("_")')
                if [ -n "${container_name}" ];then
                    local ret="${ret}\n$(cat $i |grep -v root|awk -F: '{if ($4 == 0) print $1 " || '${container_name}'"}')"
                fi
            fi
        done
    fi
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
        echo -e "$ret"
        exit 1
    fi
}

function 15_check_user_login() {
    coler green  "检查用户是否可以支持登陆"
    local ret=""
    if_tools
    if [ "$(get_cri)" == "docker" ];then
        for i in $(find /var/lib/docker/overlay2/ -name passwd|grep "/etc/passwd")
            do
            if [ -f $i ];then
                local volum_id=$(echo $i|awk -F/ '{print $6}')
                local container_name=$(docker inspect $(docker ps -qa) | jq -r 'map([.Name, .GraphDriver.Data.MergedDir]) | .[] | "\(.[0])\t\(.[1])"'|grep $volum_id|awk '{print $1}')
                local file_path=$(echo $i|awk -F$volum_id '{print $NF}')
                if [ -n "${container_name}" ];then
                    local ret="${ret}\n`cat $i |grep -v "root"|awk -F: '{if($NF != "/sbin/nologin" && $NF != "/usr/sbin/nologin" ) print  $1 " || '${container_name}'"}'`"
                fi
             fi
        done
    else
        for i in $(find /run/containerd/io.containerd.runtime.v2.task/k8s.io/ -name passwd|grep "/etc/passwd")
            do
            if [ -f $i ];then
                volum_id=$(echo $i|awk -F/ '{print $6}'|cut -b 1-13 )
                container_name=$(crictl inspect "${volum_id}" |jq -r '["", .status.labels["io.kubernetes.container.name"], .status.labels["io.kubernetes.pod.name"], .status.labels["io.kubernetes.pod.namespace"], ""] | join("_")')
                if [ -n "${container_name}" ];then
                    local file_path=$(echo $i|awk -F$volum_id '{print $NF}')
                    local ret="${ret}\n$(cat $i |grep -v "root"|awk -F: '{if($NF != "/sbin/nologin" && $NF != "/usr/sbin/nologin" && $NF != "/sbin/false") print $1 " || '${container_name}'"}')"
                fi
            fi
        done
    fi
    local ret=$(echo -e "${ret}" |sed '/^$/d')
    if [ "${ret}" != "" ];then
      echo -e "$ret"
      exit 1
    fi
}

main(){
     case $1 in
     1)
     01_net_listen
     ;;
     2)
     02_sniffing_tool
     ;;
     3)
     03_sensitive_tool_binary
     ;;
     4)
     04_sensitive_tool_file
     ;;
     5)
     05_process_root_check
     ;;
     6)
     06_container_root_check
     ;;
     7)
     07_privileged
     ;;
     8)
     08_capabilities
     ;;
     9)
     09_plaintext_transmission
     ;;
     10)
     10_container_plaintext_transmission
     ;;
     11)
     11_critical_port
     ;;
     12)
     12_sudoers_check
     ;;
     13)
     13_check_env
     ;;
     14)
     14_check_uid
     ;;
     15)
     15_check_user_login
     ;;
     *)
     usage $1
     exit 2
     ;;
     esac
}
main "$@"