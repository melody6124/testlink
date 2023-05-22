# -*- coding: utf-8 -*-
import requests

wechat_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72cd5663-9272-494f-9a0c-5c0e36341358"
msg = {
    "msgtype": "markdown",
    "markdown": {
        "content": "快下班了，任务都logtime一下吧",
    }
}
requests.post(wechat_webhook, json=msg)
