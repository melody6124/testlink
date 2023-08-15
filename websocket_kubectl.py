import base64
import ssl

import websocket

url = "wss://192.168.177.74:45443/auth/v1/pod/shell?access-token=eyJhbGciOiJSUzI1NiIsImtpZCI6ImYyZmRlMDQ1ODc4MTQ5YmEzNTcwM2Y3NDMzNzM0YjliODdlMGYyMDUifQ.eyJpc3MiOiJodHRwczovLzE5Mi4xNjguMTc3Ljc0OjQ1NDQzL2RleCIsInN1YiI6IkNpUXdPR0U0TmpnMFlpMWtZamc0TFRSaU56TXRPVEJoT1MwelkyUXhOall4WmpVME5qWVNCV3h2WTJGcyIsImF1ZCI6ImFsYXVkYS1hdXRoIiwiZXhwIjoxNjkxMDI4NTQzLCJpYXQiOjE2OTA5NDIxNDMsIm5vbmNlIjoiYWxhdWRhLWNvbnNvbGUiLCJhdF9oYXNoIjoiRUQ2MUJqdFVTRjc3VnZ0Ni1jQzdudyIsImNfaGFzaCI6IjEwNklZSVhXQkFGLWdRT3UwTHd4d2ciLCJlbWFpbCI6ImFkbWluIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInJvbGVzIjpbInBsYXRmb3JtLWFkbWluLXN5c3RlbSJdLCJuYW1lIjoiYWRtaW4iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhZG1pbiIsImV4dCI6eyJpc19hZG1pbiI6dHJ1ZSwiY29ubl9pZCI6ImxvY2FsIn19.WhIFlDH6G_CLswl8UH6xbuRFBZabN6uAipGxE0i4-q8Pk_hhFxpd5KipZ4xFHLCk4ZpuT6a_LVbjthLvvUKRpbmE8W_IeZunIpTwETyCoRMXd1BPZIgg17gT79ahJJtypob2xCRpZ5YbLHJ08LJd7FJEuzqCb-vdmx3z5EujIEmJ1yxob2DL-yzjetxaIXwbF5_salJbauGqiEgTC9G98XbsHa2-WNqs55McM6bSnCK1vQTzSni7_cNnlFEblJBZ5Q-cysN1RugU45cNVMnuMW_cCvqbf1bto0WC3bEhkQH1n_NGi4ZROJqeeZMomCnp442gpxOUNnz2vEcwWv5LYw&container=kubectl&stdin=true&stdout=true&stderr=true&tty=true&command=sh&command=-c&command=kubectl-shell.sh%20ovnovn"
ws = websocket.create_connection(url, timeout=20, sslopt={"cert_reqs": ssl.CERT_NONE})
print(base64.b64decode(ws.recv()[1::]).decode('utf-8'))
command = "kubectl get node"
encode = '0' + str(base64.b64encode(command.encode('utf-8')), 'utf-8')
ws.send(encode)
ws.send('0DQ==')
ws.recv()
ws.recv()
response = ""
cnt = 0
while "cluster-console>" not in response and cnt < 5:
    response = response + base64.b64decode(ws.recv()[1::]).decode('utf-8')
    cnt = cnt + 1
print(response)
ws.close()
