# Talent_Workbench_autojs

## 📋 项目简介

这是一个基于Django Channels的WebSocket服务器项目，用于实现Android AutoJS客户端与服务器之间的实时通信。项目通过RabbitMQ消息队列接收任务数据，并通过WebSocket将任务信息推送给指定的Android客户端执行自动化脚本。

### 🎯 核心功能

- **WebSocket实时通信**：支持Android客户端与服务器的双向实时通信
- **RabbitMQ消息队列**：接收外部系统推送的任务数据
- **任务分发机制**：根据用户ID和关联ID智能分发任务给指定客户端
- **自动化脚本执行**：Android客户端接收任务后自动下载并执行脚本
- **跨域支持**：支持前后端分离架构的跨域请求

## 🚀 快速开始

### 环境要求

- **Python版本**：Python 3.13.1
- **操作系统**：支持Windows、Linux、macOS
- **依赖服务**：RabbitMQ消息队列

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动项目

```bash
daphne -p 8003 WebSocket.asgi:application
```

项目将在8003端口启动WebSocket服务。

## 📁 项目结构说明

### consumers文件夹核心文件

`consumers`文件夹是项目的核心模块，包含以下关键文件：

#### 1. apps.py - 应用启动配置
**功能**：确保Django项目启动时自动启动RabbitMQ消费者

**主要函数**：
- `ready()`: Django应用准备就绪时调用，在后台线程中启动RabbitMQ消费者
- `start_rabbitmq_consumer()`: 启动RabbitMQ消费者的内部函数

**核心逻辑**：
```python
def ready(self):
    """Django应用准备就绪时调用"""
    # 避免重复启动
    if hasattr(self, '_rabbitmq_started'):
        return
    
    # 在后台线程中启动RabbitMQ消费者
    rabbitmq_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    rabbitmq_thread.start()
```

#### 2. consumers.py - WebSocket消费者核心逻辑
**功能**：处理WebSocket连接、消息接收和发送

**主要函数**：

- **`connect()`**: WebSocket连接建立时调用
  - 获取客户端ID并存储到缓存
  - 加入MQ广播组
  - 建立WebSocket连接

- **`receive(text_data)`**: 接收客户端消息
  - 解析JSON格式的客户端消息
  - 发送连接成功响应

- **`send_message(data)`**: 向客户端发送消息
  - 将数据转换为JSON格式发送

- **`disconnect(close_code)`**: 连接关闭时调用
  - 清理缓存中的客户端关联
  - 从广播组中移除

- **`http_message(event)`**: 处理HTTP转发的消息（新版本）
  - 接收Android端的自动化任务启动请求
  - 设置客户端userId和相关参数
  - 为后续MQ消息分发做准备

- **`mq_message(event)`**: 处理MQ消息广播
  - 接收RabbitMQ广播的任务消息
  - 根据业务逻辑判断是否发送给当前客户端
  - 支持按用户ID和关联ID进行任务分发

**核心业务逻辑**：
```python
async def mq_message(self, event):
    """处理从RabbitMQ广播过来的消息"""
    message = event['message']
    userId = message['userId']
    relatedIds = message['relatedIds']
    
    # 业务判断逻辑：检查客户端是否应该接收此任务
    if self.userId in relatedIds_list:
        await self.send_message(data)  # 发送任务给客户端
```

#### 3. utils.py - 工具类
**功能**：提供HTTP消息处理和MQ消息解析的工具函数

**主要函数**：

- **`process_http_message(message)`**: 处理HTTP消息
  - 从HTTP请求中提取指定字段
  - 返回包含token、username、userId等信息的字典

- **`process_mq_message(userid)`**: 处理MQ消息
  - 根据userid查找对应的JSON任务文件
  - 提取任务相关字段（task_code、script_url等）
  - 返回处理后的任务数据

- **`get_latest_json_file(userid)`**: 获取最新JSON文件
  - 在task_json/userid_{userid}目录下查找最新的JSON文件
  - 按文件名排序返回最新文件路径
  - 支持调试输出文件信息

- **`get_current_timestamp()`**: 获取当前时间戳
  - 返回格式化的时间戳字符串

**使用示例**：
```python
# 实例化工具类
utils = Utils()

# 处理HTTP消息
http_data = utils.process_http_message(message)

# 处理MQ消息
mq_data = utils.process_mq_message(userid)
```

## 🌐 部署配置

### Nginx反向代理配置

项目支持通过Nginx进行反向代理，实现HTTPS访问和负载均衡。以下是完整的Nginx配置示例：

```nginx
server {
    listen 80;
    listen 443 ssl;
    listen 443 quic;
    http2 on;
    server_name websocket.autojs.ljzzh.cn;
    index index.html index.htm default.htm default.html;
    root /www/wwwroot/websocket.autojs.ljzzh.cn/WebSocket;
    
    # SSL证书配置
    ssl_certificate    /www/server/panel/vhost/cert/WebSocket/fullchain.pem;
    ssl_certificate_key    /www/server/panel/vhost/cert/WebSocket/privkey.pem;
    ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_tickets on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    add_header Strict-Transport-Security "max-age=31536000";
    error_page 497  https://$host$request_uri;

    # 静态文件配置
    location /static/ {
        root /www/wwwroot/websocket.autojs.ljzzh.cn/WebSocket;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # WebSocket反向代理配置
    location /ws/ {
        proxy_pass http://127.0.0.1:8003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # HTTP接口反向代理配置
    location /consumers/ {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 60s;
    }

    # 安全配置
    location ~ ^/(\.user.ini|\.htaccess|\.git|\.svn|\.project|LICENSE|README.md|package.json|package-lock.json|\.env) {
        return 404;
    }

    access_log  /www/wwwlogs/WebSocket.log;
    error_log  /www/wwwlogs/WebSocket.error.log;
}
```

### 关键配置说明

#### 1. 静态文件配置
```nginx
location /static/ {
    root /www/wwwroot/websocket.autojs.ljzzh.cn/WebSocket;
    expires 30d;
    add_header Cache-Control "public, max-age=2592000";
}
```
- 处理Django项目的静态资源
- 设置30天缓存提升性能

#### 2. WebSocket反向代理
```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:8003;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
    proxy_send_timeout 86400;
}
```
- 将`/ws/`开头的请求转发到Daphne服务（8003端口）
- 支持WebSocket协议升级
- 设置24小时超时避免连接断开

#### 3. HTTP接口反向代理
```nginx
location /consumers/ {
    proxy_pass http://127.0.0.1:8003;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```
- 将`/consumers/`开头的业务接口转发到Daphne
- 传递必要的请求头信息


## 🔧 跨域配置

### 安装跨域支持包

```bash
pip install django-cors-headers
```

### Django设置配置

在`settings.py`中添加以下配置：

#### 1. 添加中间件
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 必须放在最前面
    # ... 其他中间件
]
```

#### 2. 注册应用
```python
INSTALLED_APPS = [
    'corsheaders',  # 添加CORS应用
    # ... 其他应用
]
```

#### 3. 设置允许的源
```python
# 格式必须完整（包含 https://），不能只写域名
CORS_ALLOWED_ORIGINS = [
    "https://autojs.ljzzh.cn",  # 前端域名（必须和报错中的origin完全一致）
    "http://localhost:8080",    # 本地开发环境（可选，方便调试）
]
```

#### 4. 设置允许的主机
```python
ALLOWED_HOSTS = [
    '*',  # 允许所有主机（生产环境建议指定具体域名）
    'websocket.autojs.ljzzh.cn',
]
```

## 📋 业务逻辑说明

### 任务分发机制

项目通过`mq_message`函数实现智能任务分发，核心逻辑如下：

#### 1. 任务接收流程
1. **RabbitMQ消息接收**：通过`receive_rabbitmq.py`接收外部系统推送的任务
2. **消息处理**：`utils.py`中的`process_mq_message`函数解析任务数据
3. **任务广播**：通过WebSocket广播组发送给所有连接的客户端
4. **条件判断**：每个客户端根据自身条件决定是否执行任务

#### 2. 执行条件判断
在`consumers.py`的`mq_message`函数中实现：

```python
async def mq_message(self, event):
    """处理MQ消息广播"""
    message = event['message']
    userId = message['userId']           # 任务目标用户ID
    relatedIds = message['relatedIds']  # 关联用户ID列表
    
    # 业务判断逻辑
    if isinstance(relatedIds, str):
        relatedIds_list = relatedIds.split(',')
        if self.userId in relatedIds_list:
            # 符合条件，发送任务给客户端
            await self.send_message(data)
        elif relatedIds_list == ['']:
            # 空列表表示广播给所有用户
            await self.send_message(data)
        else:
            # 不符合条件，不发送
            return
```

#### 3. 自定义业务逻辑

如需修改Android客户端执行脚本的条件，可在`mq_message`函数中修改判断逻辑：

**示例：添加coin数量判断**
```python
# 在mq_message函数中添加
min_coin = message.get('min_coin', 0)
client_coin = self.get_client_coin(self.userId)  # 获取客户端coin数量

if client_coin >= min_coin and self.userId in relatedIds_list:
    await self.send_message(data)
```

**示例：添加用户权限判断**
```python
# 检查用户权限
if self.check_user_permission(self.userId) and self.userId in relatedIds_list:
    await self.send_message(data)
```

### 数据流转过程

1. **外部系统** → **RabbitMQ** → **receive_rabbitmq.py**
2. **receive_rabbitmq.py** → **utils.py** → **consumers.py**
3. **consumers.py** → **WebSocket广播** → **Android客户端**
4. **Android客户端** → **下载脚本** → **执行自动化任务**

## 🛠️ 开发指南

### 修改任务执行条件

如需自定义任务分发逻辑，主要修改以下文件：

1. **`consumers.py`** - 修改`mq_message`函数中的业务判断逻辑
2. **`utils.py`** - 添加新的工具函数支持业务判断
3. **`receive_rabbitmq.py`** - 修改消息接收和处理逻辑

### 添加新的API接口

1. 在`consumers/urls.py`中添加路由
2. 在`consumers/views.py`中添加视图函数
3. 在`consumers/consumers.py`中添加对应的WebSocket处理函数

### 调试建议

1. **日志输出**：项目已添加详细的日志输出，便于调试
2. **文件监控**：监控`task_json`目录下的JSON文件变化
3. **WebSocket连接**：使用浏览器开发者工具监控WebSocket连接状态
4. **RabbitMQ监控**：使用RabbitMQ管理界面监控消息队列状态

## 📝 总结

本项目是一个完整的WebSocket服务器解决方案，实现了Android AutoJS客户端与服务器之间的实时通信。通过RabbitMQ消息队列和WebSocket技术，实现了高效的任务分发和自动化脚本执行。

### 主要特性

- ✅ **实时通信**：基于WebSocket的双向实时通信
- ✅ **消息队列**：RabbitMQ支持高并发消息处理
- ✅ **智能分发**：根据用户ID和业务条件智能分发任务
- ✅ **跨域支持**：完整的CORS配置支持前后端分离
- ✅ **反向代理**：Nginx配置支持HTTPS和负载均衡
- ✅ **易于扩展**：模块化设计，便于添加新功能

### 技术栈

- **后端框架**：Django + Django Channels
- **WebSocket服务**：Daphne
- **消息队列**：RabbitMQ
- **反向代理**：Nginx
- **Python版本**：3.13.1

### 联系方式

如有问题或建议，请通过GitHub Issues联系。

---

**注意**：本项目仅供学习和研究使用，请遵守相关法律法规。

