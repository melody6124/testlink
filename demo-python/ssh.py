import argparse

import paramiko

parser = argparse.ArgumentParser(description='ssh sample')
parser.add_argument('-H', '--host', default='192.168.176.121')
parser.add_argument('--name', default="root")
parser.add_argument('--password', default="")
parser.add_argument('--key_path', default="./tx")
parser.add_argument('--port', default="22")
args = parser.parse_args()


# 登录到远端
def connect(host, password, key_path='', port=22, name='root'):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if len(password) > 0:
        client.connect(hostname=host, port=int(port), username=name, password=password, timeout=18000)
    else:
        key = paramiko.RSAKey.from_private_key_file(key_path)
        client.connect(hostname=host, port=int(port), username=name, pkey=key, timeout=18000)
    return client


# 执行命令
def exec_command(client, command):
    stdin, stdout, stderr = client.exec_command(command, timeout=18000, get_pty=True)
    result = (stdout.channel.recv_exit_status(), str(stdout.read()), str(stderr.read()))
    print("excute_script cmd is: {}".format(command))
    print("excute_script cmd result is: {}".format(result))
    client.close()
    return result


def sftp_file(client, localpath, remotepath, action):
    sftp = client.open_sftp()
    try:
        if action == 'upload':
            # 本地文件上传到远端
            sftp.put(localpath, remotepath)
        elif action == 'download':
            # 远端文件下载到本地
            sftp.get(remotepath, localpath)
    except Exception as e:
        print(f"sftp {action} failed {e}")
    sftp.close()


if __name__ == '__main__':
    client = connect(args.host, args.password, args.key_path)
    sftp_file(client, './tx', './uptx', 'upload')
    exec_command(client, 'ls ./')
    sftp_file(client, './downtx', './uptx', 'download')
