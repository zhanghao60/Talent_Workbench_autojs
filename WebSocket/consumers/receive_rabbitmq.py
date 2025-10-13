import pika
import json
import time
import signal
import sys
import re
import datetime
import os
from .utils import Utils

utils = Utils()

# 全局变量，模拟原代码中的全局消费状态
全局消费状态 = True

# 指定的脚本目录
脚本目录 = "/sdcard/trmkt/"

# RabbitMQ连接配置
连接配置 = {
    '主机': '118.178.32.102',
    '端口': 5672,
    '用户名': 'guest',
    '密码': 'guest',
    '队列名': 'rpa_task'
}

def 创建连接():
    """创建RabbitMQ连接和通道"""
    try:
        凭据 = pika.PlainCredentials(连接配置['用户名'], 连接配置['密码'])
        连接参数 = pika.ConnectionParameters(
            host=连接配置['主机'],
            port=连接配置['端口'],
            credentials=凭据
        )
        连接 = pika.BlockingConnection(连接参数)
        通道 = 连接.channel()
        
        # 确保队列存在
        通道.queue_declare(queue=连接配置['队列名'], durable=True)
        print(f"队列{连接配置['队列名']}已创建")
        
        return 连接, 通道
    except Exception as 异常:
        print(f'创建连接失败: {str(异常)}')
        return None, None

def 处理消息(通道, 方法, 消息体, 消息接收回调):
    """处理单个消息"""
    global 全局消费状态
    
    if not 消息体 or not 全局消费状态:
        return
    
    try:
        消息内容 = 消息体.decode()
        print(f"收到消息")
        
        # 解析消息体
        try:
            消息对象 = json.loads(消息内容)
        except json.JSONDecodeError:
            通道.basic_nack(delivery_tag=方法.delivery_tag)
            return

        
        try:
            # 执行消息处理
            消息接收回调(消息对象)
            print('[✓] 消息处理成功')
            通道.basic_ack(delivery_tag=方法.delivery_tag)
        except Exception as 处理错误:
            print(f'[✗] 消息处理失败: {str(处理错误)}')
            通道.basic_nack(delivery_tag=方法.delivery_tag)

    except Exception as 异常:
        if 通道:
            通道.basic_nack(delivery_tag=方法.delivery_tag)

def 创建消息回调(消息接收回调):
    """创建消息处理回调函数"""
    def 回调函数(通道, 方法, 属性, 消息体):
        处理消息(通道, 方法, 消息体, 消息接收回调)
    
    return 回调函数

def 创建关闭处理器(连接, 通道):
    """创建关闭信号处理函数"""
    def 处理关闭(信号号, 帧):
        print('\n正在关闭消费者...')
        
        if 通道 and 通道.is_open:
            通道.stop_consuming()
            通道.close()
        if 连接 and 连接.is_open:
            连接.close()
        
        print('消费者已成功关闭。')
        sys.exit(0)
    
    return 处理关闭

def 处理嵌套JSON(数据):
    """递归处理嵌套的JSON字符串，将其解析为JSON对象"""
    if isinstance(数据, dict):
        # 如果是字典，递归处理每个值
        处理后的字典 = {}
        for 键, 值 in 数据.items():
            处理后的字典[键] = 处理嵌套JSON(值)
        return 处理后的字典
    elif isinstance(数据, list):
        # 如果是列表，递归处理每个元素
        return [处理嵌套JSON(元素) for 元素 in 数据]
    elif isinstance(数据, str):
        # 如果是字符串，尝试解析为JSON
        try:
            # 尝试解析为JSON
            parsed = json.loads(数据)
            # 如果解析成功，递归处理解析后的数据
            return 处理嵌套JSON(parsed)
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，检查是否是键值对格式的字符串
            if ':' in 数据 and 数据.startswith('"') and 数据.endswith('"'):
                try:
                    # 尝试解析为键值对
                    # 移除首尾的双引号
                    内容 = 数据[1:-1]
                    # 查找第一个冒号
                    冒号位置 = 内容.find(':')
                    if 冒号位置 > 0:
                        键 = 内容[:冒号位置].strip('"')
                        值 = 内容[冒号位置+1:].strip()
                        # 尝试解析值
                        try:
                            解析后的值 = json.loads(值)
                            return {键: 解析后的值}
                        except:
                            return {键: 值}
                except:
                    pass
            # 如果都解析失败，返回原始字符串
            return 数据
    else:
        # 其他类型直接返回
        return 数据

def 处理customParams字段(数据):
    """专门处理customParams字段，解析其中的键值对字符串"""
    if isinstance(数据, dict):
        处理后的字典 = {}
        for 键, 值 in 数据.items():
            if 键 == 'customParams' and isinstance(值, list):
                # 处理customParams数组
                处理后的数组 = []
                for 项 in 值:
                    if isinstance(项, str):
                        # 如果是字符串，直接解析
                        解析结果 = 解析键值对字符串(项)
                        处理后的数组.append(解析结果)
                    elif isinstance(项, dict) and 'value' in 项:
                        # 如果是对象且有value字段
                        值内容 = 项['value']
                        if isinstance(值内容, str):
                            解析结果 = 解析键值对字符串(值内容)
                            处理后的数组.append(解析结果)
                        elif isinstance(值内容, dict):
                            # 如果value是对象，直接使用value的内容
                            处理后的数组.append(处理customParams字段(值内容))
                        else:
                            # 其他情况，递归处理
                            处理后的数组.append(处理customParams字段(项))
                    else:
                        # 其他情况，递归处理
                        处理后的数组.append(处理customParams字段(项))
                处理后的字典[键] = 处理后的数组
            else:
                处理后的字典[键] = 处理customParams字段(值)
        return 处理后的字典
    elif isinstance(数据, list):
        return [处理customParams字段(元素) for 元素 in 数据]
    elif isinstance(数据, str):
        # 处理字符串中的转义字符
        return 清理转义字符(数据)
    else:
        return 数据

def 清理转义字符(字符串):
    """清理字符串中的转义字符"""
    if not isinstance(字符串, str):
        return 字符串
    
    
    # 使用正则表达式将 "\" 替换为 "
    处理后的字符串 = re.sub(r'"\\"', '"', 字符串)
    
    # 如果字符串以双引号开头，移除开头的双引号
    if 处理后的字符串.startswith('"'):
        处理后的字符串 = 处理后的字符串[1:]
    
    
    return 处理后的字符串

def 解析键值对字符串(字符串):
    """解析形如 "min":3000 或 "\"min\":3000" 的字符串"""
    if not isinstance(字符串, str):
        return 字符串
    
    
    # 检查是否包含冒号
    if ':' not in 字符串:
        return 字符串
    
    try:
        # 查找第一个冒号
        冒号位置 = 字符串.find(':')
        if 冒号位置 <= 0:
            return 字符串
        
        # 提取键和值
        键名部分 = 字符串[:冒号位置].strip()
        键值部分 = 字符串[冒号位置+1:].strip()
        
        
        # 处理键名
        if 键名部分.startswith('"') and 键名部分.endswith('"'):
            键名 = 键名部分[1:-1]
        elif 键名部分.startswith('\\"') and 键名部分.endswith('\\"'):
            键名 = 键名部分[2:-2]
        else:
            键名 = 键名部分.strip('"')
        
        # 处理键值
        if 键值部分.startswith('"') and 键值部分.endswith('"'):
            键值 = 键值部分[1:-1]
        elif 键值部分.isdigit():
            键值 = int(键值部分)
        elif '.' in 键值部分 and 键值部分.replace('.', '').isdigit():
            键值 = float(键值部分)
        else:
            键值 = 键值部分
        
        
        结果 = {键名: 键值}
        return 结果
        
    except Exception as e:
        return 字符串

def 处理转义字符(字符串):
    """处理字符串中的转义字符"""
    if not isinstance(字符串, str):
        return 字符串
    
    # 替换常见的转义字符
    处理后的字符串 = 字符串.replace('\\"', '"')  # 替换 \" 为 "
    处理后的字符串 = 处理后的字符串.replace('\\\\', '\\')  # 替换 \\ 为 \
    处理后的字符串 = 处理后的字符串.replace('\\n', '\n')  # 替换 \n 为换行
    处理后的字符串 = 处理后的字符串.replace('\\t', '\t')  # 替换 \t 为制表符
    
    return 处理后的字符串

def 最终清理转义字符(数据):
    """递归处理数据结构中的所有转义字符"""
    if isinstance(数据, dict):
        处理后的字典 = {}
        for 键, 值 in 数据.items():
            处理后的字典[键] = 最终清理转义字符(值)
        return 处理后的字典
    elif isinstance(数据, list):
        return [最终清理转义字符(元素) for 元素 in 数据]
    elif isinstance(数据, str):
        # 使用简单的字符串替换处理转义字符
        处理后的字符串 = 数据.replace('"\\"', '"')  # 将 "\" 替换为 "
        处理后的字符串 = 处理后的字符串.replace('\\"', '"')  # 将 \" 替换为 "
        处理后的字符串 = 处理后的字符串.replace('\\\\', '\\')  # 将 \\ 替换为 \
        return 处理后的字符串
    else:
        return 数据

def 示例消息接收回调(消息):
    
    时间戳 = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建基础文件夹结构
    基础文件夹 = "task_json"
    if not os.path.exists(基础文件夹):
        os.makedirs(基础文件夹)
    
    # 检查是否是任务数组
    if isinstance(消息, list):
        print("这是任务数组")
    else:
        print("接收到mq消息")
        print("这是单个任务")
        # 处理单个任务
        任务ID = 消息.get('taskId', 'single_task')
        userId = 消息.get('userId', 'unknown')
        
        # 创建用户文件夹
        用户文件夹 = os.path.join(基础文件夹, f'userid_{userId}')
        if not os.path.exists(用户文件夹):
            os.makedirs(用户文件夹)
        
        # 文件名格式：时间戳.json
        文件名 = os.path.join(用户文件夹, f'{时间戳}.json')
        
        with open(文件名, 'w', encoding='utf-8') as f:
            # 先处理嵌套的JSON字符串
            处理后的消息 = 处理嵌套JSON(消息)
            # 再专门处理customParams字段
            最终消息 = 处理customParams字段(处理后的消息)
            
            # 使用json.dumps确保中文字符正确显示
            json_str = json.dumps(最终消息, ensure_ascii=False, indent=4, separators=(',', ': '))
            f.write(json_str)
        print(f'任务 {任务ID} 已保存到文件: {文件名}')
    
    # 处理逻辑
    mq_data = utils.process_mq_message(userId)
    广播mq消息(mq_data)

def 广播mq消息(消息):
    """
    将MQ消息广播给所有已连接的WebSocket客户端
    
    Args:
        消息: 要广播的MQ消息数据
    """
    print("将mq消息广播给所有已经连接的websocket对象")
    
    try:
        # 导入必要的模块
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        # 获取channel layer
        channel_layer = get_channel_layer()
        if not channel_layer:
            print("错误：无法获取channel layer")
            return
        
        # 准备广播消息
        broadcast_message = {
            'type': 'mq_message',  # 消息类型，对应consumers.py中的mq_message方法
            'message': 消息  # MQ消息内容
        }
        
        # 使用Django Channels的组广播功能
        # 这会自动发送给所有在"mq_broadcast_group"组中的WebSocket连接
        async_to_sync(channel_layer.group_send)(
            "mq_broadcast_group",  # 组名
            broadcast_message
        )
        
        print("MQ消息已成功广播给所有已连接的WebSocket客户端")
        
    except ImportError as e:
        print(f"导入模块失败: {str(e)}")
        print("请确保Django Channels已正确安装和配置")
    except Exception as e:
        print(f"广播MQ消息时发生未知错误: {str(e)}")

def main(消息接收回调, 启用信号处理=True):
    连接 = None
    通道 = None
    
    # 只在主线程中注册信号处理器
    if 启用信号处理:
        try:
            关闭处理器 = 创建关闭处理器(连接, 通道)
            signal.signal(signal.SIGINT, 关闭处理器)
            signal.signal(signal.SIGTERM, 关闭处理器)
        except ValueError:
            # 在非主线程中会抛出这个异常，忽略即可
            print("信号处理已跳过（非主线程）")
    
    while True:  # 添加重连循环
        try:
            连接, 通道 = 创建连接()
            if not 连接 or not 通道:
                raise Exception("连接创建失败")
            print("连接成功")
            print('全局消费状态:', 全局消费状态)
            print('等待消息中。按CTRL+C退出')
            
            if 全局消费状态 and 通道:
                # 创建消息回调
                回调函数 = 创建消息回调(消息接收回调)
                # 开始消费消息
                通道.basic_consume(
                    queue=连接配置['队列名'],
                    on_message_callback=回调函数,
                    auto_ack=False  # 手动确认消息
                )
                # 开始消费循环
                if 全局消费状态:
                    通道.start_consuming()
                    
        # 捕获异常
        except Exception as 异常:
            print(f'连接错误: {str(异常)}')
            print("连接失败，5秒后重试...")
            
            # 清理资源
            if 通道 and 通道.is_open:
                try:
                    通道.close()
                except:
                    pass
            if 连接 and 连接.is_open:
                try:
                    连接.close()
                except:
                    pass
            
            # 等待5秒后重连
            time.sleep(5)
            continue

# 只有在直接运行此文件时才执行main函数
if __name__ == "__main__":
    main(示例消息接收回调)

