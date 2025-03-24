from flask import Flask, jsonify, request
import http.client
import json
import os

app = Flask(__name__)

# 根据提供的邮箱地址获取验证码
def get_verification_code(email):
    # 创建连接
    conn = http.client.HTTPSConnection("domain-open-api.cuiqiu.com")

    # 构造 multipart/form-data 请求的内容
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    dataList = []

    # 添加多个表单字段
    fields = {
        "token": "6153f3883c3b4521a70090d4e4b6e6d0",
        "folder": "Inbox",
        "mail_id": "1732607589833756811",
        "start_time": "2024-05-01",
        "end_time": "2025-03-24",
        "page": "1",
        "limit": "10",
        "to": email
    }

    for name, value in fields.items():
        dataList.append(f'--{boundary}\r\n'.encode())
        dataList.append(f'Content-Disposition: form-data; name="{name}"\r\n'.encode())
        dataList.append(b'Content-Type: text/plain\r\n\r\n')
        dataList.append(f'{value}\r\n'.encode())

    # 完成请求的结束标记
    dataList.append(f'--{boundary}--\r\n'.encode())

    # 构建请求体
    body = b''.join(dataList)

    # 设置请求头
    headers = {
        'Content-type': f'multipart/form-data; boundary={boundary}'
    }

    # 发送 POST 请求
    conn.request("POST", "/v1/message/list", body, headers)

    # 获取响应
    res = conn.getresponse()
    data = res.read()

    # 返回解析后的响应数据
    return json.loads(data.decode("utf-8"))

# 路由处理
@app.route('/get_code/<email>', methods=['GET'])
def get_code(email):
    try:
        # 获取验证码邮件数据
        response_data = get_verification_code(email)
        
        # 检查响应状态码是否为 200
        if response_data.get("code") == 200:
            emails = response_data.get("data", {}).get("list", [])
            
            if not emails:
                return jsonify({
                    "status": "error",
                    "message": "No emails found"
                }), 404
            
            # 获取最新一封邮件（假设列表按时间降序排列）
            latest_email = emails[0]
            
            # 提取所需字段
            result = {
                "time": latest_email.get("time", ""),
                "email": latest_email.get("to", [{}])[0].get("address", ""),
                "code": latest_email.get("subject", "")
            }
            
            return jsonify(result), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to retrieve emails"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # 启动 Flask 应用，确保监听所有外部请求
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))  # Railway 会自动设置环境变量 PORT
