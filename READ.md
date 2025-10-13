项目说明：

consumers文件夹里面的apps.py保证项目启动的时候，也同时启动mq消费者，从而实现接受http请求，转发给websocket，进而运行脚本

项目启动命令:
daphne -p 8003 WebSocket.asgi:application

python版本：
Python 3.13.1

依赖安装命令
pip install -r requirements.txt

nginx反向代理配置示例：

server
{
    listen 80;
    listen 443 ssl;
    listen 443 quic;
    http2 on;
    server_name websocket.autojs.ljzzh.cn;
    index index.html index.htm default.htm default.html;
    root /www/wwwroot/websocket.autojs.ljzzh.cn/WebSocket;
    #CERT-APPLY-CHECK--START
    # 用于SSL证书申请时的文件验证相关配置 -- 请勿删除
    include /www/server/panel/vhost/nginx/well-known/WebSocket.conf;
    #CERT-APPLY-CHECK--END

    #SSL-START SSL相关配置
    #error_page 404/404.html;
    ssl_certificate    /www/server/panel/vhost/cert/WebSocket/fullchain.pem;
    ssl_certificate_key    /www/server/panel/vhost/cert/WebSocket/privkey.pem;
    ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_tickets on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    add_header Strict-Transport-Security "max-age=31536000";
    add_header Alt-Svc 'quic=":443"; h3=":443"; h3-29=":443"; h3-27=":443";h3-25=":443"; h3-T050=":443"; h3-Q050=":443";h3-Q049=":443";h3-Q048=":443"; h3-Q046=":443"; h3-Q043=":443"';
    error_page 497  https://$host$request_uri;

    
    #SSL-END

    #ERROR-PAGE-START  错误页相关配置
    #error_page 404 /404.html;
    #error_page 502 /502.html;
    #ERROR-PAGE-END


    #REWRITE-START 伪静态相关配置
    include /www/server/panel/vhost/rewrite/python_WebSocket.conf;
    #REWRITE-END

    #禁止访问的文件或目录
    location ~ ^/(\.user.ini|\.htaccess|\.git|\.svn|\.project|LICENSE|README.md|package.json|package-lock.json|\.env) {
        return 404;
    }

    #一键申请SSL证书验证目录相关设置
    location /.well-known/ {
        root /www/wwwroot/java_node_ssl;
    }

    #禁止在证书验证目录放入敏感文件
    if ( $uri ~ "^/\.well-known/.*\.(php|jsp|py|js|css|lua|ts|go|zip|tar\.gz|rar|7z|sql|bak)$" ) {
        return 403;
    }

    # HTTP反向代理相关配置开始 >>>
    location ~ /purge(/.*) {
        proxy_cache_purge cache_one 127.0.0.1$request_uri$is_args$args;
    }

    # proxy
    # -------------------------- 新增配置开始 --------------------------
    # 1. 静态文件配置：处理 Django 项目的 static 目录（前端静态资源）
    location /static/ {
        # 指向 Django 项目的 static 目录（确保该目录存在且有资源）
        root /www/wwwroot/websocket.autojs.ljzzh.cn/WebSocket;
        expires 30d;  # 静态资源缓存 30 天，提升性能
        add_header Cache-Control "public, max-age=2592000";
    }

    # 2. WebSocket 反向代理：将 /ws/ 开头的请求转发到 Daphne（监听 8003 端口）
    location /ws/ {
        proxy_pass http://127.0.0.1:8003;  # Daphne 服务地址（本地监听，安全）
        proxy_http_version 1.1;  # 必须使用 HTTP/1.1 支持 WebSocket 升级
        # 关键：告知 Nginx 升级协议为 WebSocket
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        # 传递真实域名和客户端 IP
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;  # 传递 HTTPS 协议标识
        proxy_read_timeout 86400;  # 延长超时时间（24小时），避免 WebSocket 连接被断开
        proxy_send_timeout 86400;
    }

    # 3. HTTP 接口反向代理：将 /consumers/ 开头的业务接口转发到 Daphne
    location /consumers/ {
        proxy_pass http://127.0.0.1:8003;  # 同 WebSocket 转发地址
        # 传递必要的请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;  # 连接超时时间
        proxy_read_timeout 60s;     # 读取超时时间
    }
    # HTTP反向代理相关配置结束 <<<

    access_log  /www/wwwlogs/WebSocket.log;
    error_log  /www/wwwlogs/WebSocket.error.log;
}


关键配置：

    # -------------------------- 反向代理新增配置开始 --------------------------
    # 1. 静态文件配置：处理 Django 项目的 static 目录（前端静态资源）
    location /static/ {
        # 指向 Django 项目的 static 目录（确保该目录存在且有资源）
        root /www/wwwroot/websocket.autojs.ljzzh.cn/WebSocket;
        expires 30d;  # 静态资源缓存 30 天，提升性能
        add_header Cache-Control "public, max-age=2592000";
    }

    # 2. WebSocket 反向代理：将 /ws/ 开头的请求转发到 Daphne（监听 8003 端口）
    location /ws/ {
        proxy_pass http://127.0.0.1:8003;  # Daphne 服务地址（本地监听，安全）
        proxy_http_version 1.1;  # 必须使用 HTTP/1.1 支持 WebSocket 升级
        # 关键：告知 Nginx 升级协议为 WebSocket
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        # 传递真实域名和客户端 IP
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;  # 传递 HTTPS 协议标识
        proxy_read_timeout 86400;  # 延长超时时间（24小时），避免 WebSocket 连接被断开
        proxy_send_timeout 86400;
    }

    # 3. HTTP 接口反向代理：将 /consumers/ 开头的业务接口转发到 Daphne
    location /consumers/ {
        proxy_pass http://127.0.0.1:8003;  # 同 WebSocket 转发地址
        # 传递必要的请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;  # 连接超时时间
        proxy_read_timeout 60s;     # 读取超时时间
    }
    # HTTP反向代理相关配置结束 <<<

关键的一共就3个配置，剩下的就是配置域名，证书之类
我这里的配置是有证书的情况下，https请求

注意处理跨域问题，前端和后端的域名不一致
pip install django-cors-headers

添加中间件
'corsheaders.middleware.CorsMiddleware', 

注册app
'corsheaders',  

设置cors
# 格式必须完整（包含 https://），不能只写 'autojs.ljzzh.cn'
CORS_ALLOWED_ORIGINS = [
    "https://autojs.ljzzh.cn",  # 你的前端域名（必须和报错中的 origin 完全一致）
    "http://localhost:8080",    # 本地开发环境（可选，方便调试）
]

设置host
ALLOWED_HOSTS = [
    '*',
    'websocket.autojs.ljzzh.cn',
]


consumers文件夹下面的utils.py文件是工具类，里面封装了消息处理的函数
如果要更改安卓客户端执行脚本的条件，比如判断coin数量是否满足，是否满足客户端指定的userid，就在mq_message函数里面更改