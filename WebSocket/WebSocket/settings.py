from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-dcz&4vi44g8b^q#&u@s8%wkgjxrj#npn%+vbt2%=q%%!t9^p@b"

# 设置调试模式
DEBUG = True

# 设置静态文件url
STATIC_URL = "static/"

# 设置允许的域名
ALLOWED_HOSTS = [
    '*',
    'websocket.autojs.ljzzh.cn',
    'autojs.ljzzh.cn',
]

# CORS设置 - 允许所有域名（开发环境）
# 注意：生产环境建议限制为特定域名以提高安全性
CORS_ALLOW_ALL_ORIGINS = True  # 允许所有域名进行跨域请求

# CORS设置 - 如果只允许特定域名，可以注释掉上面一行，使用下面的配置
# CORS_ALLOWED_ORIGINS = [
#     "https://autojs.ljzzh.cn",
#     "http://localhost:8080",
# ]

# CSRF设置 - 允许所有域名（开发环境）
# 注意：CSRF_TRUSTED_ORIGINS 不支持通配符，需要完整URL
# 如果允许所有域名，可以在视图中使用 @csrf_exempt 装饰器
# 这里保留一些常用的域名
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://localhost:8080',
    "https://autojs.ljzzh.cn",
]

# 注册app
INSTALLED_APPS = [
    "corsheaders",  # 添加CORS应用
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "consumers",
]

# 注册中间件
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # 添加CORS中间件
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 设置数据库
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 替换默认的ASGIApplication
ASGI_APPLICATION = "WebSocket.asgi.application"

# 配置通道层(开发环境使用内存通道层)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# 配置通道层(生产环境使用Redis通道层)
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#         },
#     },
# }

# 允许null origin（用于file://协议）
CSRF_COOKIE_SECURE = False

CSRF_COOKIE_HTTPONLY = False

ROOT_URLCONF = "WebSocket.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "WebSocket.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# 设置时区
LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = True

# 设置默认自动字段类型
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
