from django.apps import AppConfig
import threading
import os
import sys

# 保证项目启动的情况下，同时启动RabbitMQ消费者
class ConsumersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "consumers"
    
    def ready(self):
        """Django应用准备就绪时调用"""
        # 避免重复启动（检查是否已经启动过）
        if hasattr(self, '_rabbitmq_started'):
            return
        
        # 标记为已启动
        self._rabbitmq_started = True
        
        # 导入RabbitMQ消费者
        from .receive_rabbitmq import main, 示例消息接收回调
        
        # 在后台线程中启动RabbitMQ消费者
        def start_rabbitmq_consumer():
            try:
                print("正在启动RabbitMQ消费者...")
                main(示例消息接收回调, 启用信号处理=False)
            except Exception as e:
                print(f"RabbitMQ消费者启动失败: {e}")
        
        # 创建并启动后台线程
        rabbitmq_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
        rabbitmq_thread.start()
        print("RabbitMQ消费者已在后台启动")
