import os
import webbrowser
import threading
from flask import Flask, redirect, request, session, jsonify
from flask_cors import CORS
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
app.secret_key = os.urandom(24)  # 安全随机密钥

# Google OAuth配置 
GOOGLE_CLIENT_ID = '201133083213-jrbbbdvhu116cf7kdltrnatfd8funjv5.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'AIzaSyCj4ykBXBXfOQt2V8n93fxyhafhQSu9EvM'  # 从Google开发者控制台获取
GOOGLE_REDIRECT_URI = 'http://localhost:5000/callback'

@app.route('/login')
def google_login():
    # 构建Google OAuth授权URL
    auth_url = (
        f'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={GOOGLE_CLIENT_ID}&'
        f'redirect_uri={GOOGLE_REDIRECT_URI}&'
        f'response_type=code&'
        f'scope=openid%20email%20profile&'
        f'access_type=offline'
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    try:
        # 处理Google回调
        code = request.args.get('code')
        
        # 交换访问令牌
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        tokens = token_response.json()
        
        # 获取用户信息
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            headers={'Authorization': f'Bearer {tokens["access_token"]}'}
        )
        user_info = user_info_response.json()
        
        # 存储用户信息到会话
        session['user'] = user_info
        
        # 重定向到前端页面
        return redirect('http://localhost:8000/dashboard')
    
    except Exception as e:
        app.logger.error(f"Callback error: {str(e)}")
        return jsonify({"error": "Authentication failed"}), 500

@app.route('/user')
def get_user():
    # 获取当前登录用户信息
    if 'user' in session:
        return jsonify(session['user'])
    return jsonify({"error": "未登录"}), 401

@app.route('/logout')
def logout():
    # 注销登录
    session.pop('user', None)
    return jsonify({"message": "已注销"})

def run_backend_server(port=5000):
    print(f"后端服务器运行在 http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

def run_frontend_server(port=8000):
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    
    # 切换到项目目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    # 创建HTTP服务器
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', port), handler)

    print(f"前端服务器运行在 http://localhost:{port}")
    webbrowser.open(f'http://localhost:{port}')
    
    # 启动服务器
    httpd.serve_forever()

def main():
    # 后端服务器线程
    backend_thread = threading.Thread(target=run_backend_server, daemon=True)
    backend_thread.start()

    # 前端服务器
    run_frontend_server()

if __name__ == '__main__':
    main()