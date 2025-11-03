import json
import re
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache  # 导入django的缓存系统
from .utils import Utils

# 实例化工具类
utils = Utils()

# 接口类，用于处理WebSocket连接和消息
class Consumers(AsyncWebsocketConsumer):
    # 1.连接建立时调用
    async def connect(self):
        # 初始化安卓客户端属性
        self.userId = "" # 安卓端的userId
        self.relatedIds = {} # 安卓端关联id(字典类型)
        # 获取客户端ID,也就是用户名，例如456456，用户指定广播对象，对象连接websocket的时候都会分配一个这个id
        self.client_id = self.scope['url_route']['kwargs']['client_id']
        print("=============")
        print("已经连接客户端")
        print(f'客户端ID：{self.client_id}')
        print("=============")
        # 将client_id与channel_name关联存储，用于将前端的http请求转发给指定的客户端
        # 格式是 ws_456456与通道名称相关联
        cache.set(f"ws_{self.client_id}", self.channel_name, 3600)
        # 加入广播组，用于接收MQ消息广播
        self.group_name = "mq_broadcast_group"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        # 接受ws请求
        await self.accept()

    # 2.服务端接收autojs消息
    async def receive(self, text_data=None):
        # 将json字符串解析为字典
        data = json.loads(text_data)
        print(f'客户端ID:{self.client_id}发来的消息：{data}')
        response = {
            "type":"server_message",
            "message":"连接成功！"
        }
        # 回复安卓客户端
        await self.send_message(response)

    # 3. 服务端向autojs发送消息
    async def send_message(self,data):
        # 将python字典转为json字符串
        json_data = json.dumps(data)
        await self.send(text_data=json_data)

    # 4. 连接关闭时调用
    async def disconnect(self, close_code):
        # 移除关联
        cache.delete(f"ws_{self.client_id}")
        # 从广播组中移除
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # # http转发给autojs（老版本）
    # async def http_message(self, event): # 函数名要和视图中的type一致
    #     # event是从视图转发过来的字典，包含'message'字段
    #     message = event['message']  # message即HTTP请求中的JSON数据
    #     print(f'http请求发过来的消息：{message}')
        
    #     # 调用工具类处理消息，提取指定字段
    #     http_data = utils.process_http_message(message)
    #     print(f'提取的http_data：{http_data}')
        
    #     # userId = http_data['userId']
    #     关联id = http_data['关联ID']
    #     print(f'关联id：{关联id}')
    #     # 关联id：{'ids': ['106', '115'], 'count': 2}
    #     if 关联id != {}:
    #         userId_list = 关联id['ids']
    #         for userId in userId_list:
    #             try:
    #                 mq_data = utils.process_mq_message(userId)
    #                 print(f'提取的mq_data：{mq_data}')
    #                 data = {
    #                     "http_data": http_data,
    #                     "mq_data": mq_data
    #                 }
    #                 await self.send_message(data)
    #             except Exception as e:
    #                 print(f'处理用户{userId}的mq_data时发生错误：{e}')
    #     else:
    #         print("id为空，无法获取mq_data")

    # http转发给autojs（新版本）用于开启自动化服务，指定websocket对象，前端点击开始自动化任务按钮之后，发送请求过来，会自动调用此函数
    # 此函数调用之后，会给 self.userId赋值，赋值之后，代表这个对象开启了自动化任务，后续的mq消息会根据条件来判断是否广播给这个对象
    async def http_message(self, event): 
        try:
            message = event.get('message', {})
            print(f'来自安卓端的消息：{message}')
            
            # 检查必要字段是否存在
            if not isinstance(message, dict):
                print(f'错误：message 不是字典类型，实际类型：{type(message)}')
                return
            
            # 使用 get 方法安全获取字段，避免 KeyError
            self.userId = message.get('userId')
            if self.userId is None:
                print('错误：消息中缺少 userId 字段')
                return
            
            # 将userId转为字符串类型
            # 把userId转换成字符串，保证后续比较时不会因为类型不同出错
            self.userId = str(self.userId)
            print(f"安卓端userId：{self.userId}")
            
            username = message.get('username', '')
            print(f"安卓端username：{username}")
            
            最低任务佣金 = message.get('最低任务佣金', '')
            print(f"安卓端最低任务佣金：{最低任务佣金}")
            
            关联ID = message.get('关联ID', {})
            print(f"安卓端关联ID：{关联ID}")
            print(f"安卓端关联id的类型{type(关联ID)}")
            
            self.relatedIds = 关联ID if isinstance(关联ID, dict) else {}
            
            data = {
                "userId": self.userId,
                "username": username,
                "最低任务佣金": 最低任务佣金,
                "关联ID": 关联ID
            }
            print("data：", data)
        except Exception as e:
            print(f'处理 http_message 时发生错误：{e}')
            import traceback
            traceback.print_exc()
        

    # MQ消息广播处理
    async def mq_message(self, event):
        """
        处理从RabbitMQ广播过来的消息
        """
        message = event['message']  # 经过处理之后的MQ消息内容
        # 构造发送给安卓的数据格式，包含脚本下载地址
        data = {
            "mq_data": message
        }

        # 业务处理逻辑
        print(f'收到MQ广播消息，客户端username: {self.client_id}')
        print(f'MQ消息内容: {message}')
        userId = message['userId']
        print(f"服务器userId：{userId}")
        relatedIds = message['relatedIds']
        print(f"服务器relatedIds：{relatedIds}")
        android_exe_status = message['android_exe_status']
        print(f"服务器android_exe_status：{android_exe_status}")
        start_time = message['start_time']
        print(f"服务器start_time：{start_time}")
        end_time = message.get('end_time', '')
        print(f"服务器end_time：{end_time}")
        print("服务器relatedIds：", relatedIds)
        print("服务器relatedIds的类型：",type(relatedIds))
        print("客户端userId的类型:",type(self.userId))
        if isinstance(relatedIds,int):
            print("服务器的关联id类型是整数")
            print("开始将服务器的服务器relatedIds的类型改为str")
            relatedIds = str(relatedIds)
            print("类型更改更改之后")
            print(f"服务器的关联ids：{relatedIds}")
        print("客户端的userId:",self.userId)
        # 下面就是判断是否应该发送消息给安卓客户端，让安卓执行脚本的业务逻辑，如果需要更改业务逻辑，请修改下面的部分
        if isinstance(relatedIds, str):
            print("服务器的关联ids类型是字符串")
            relatedIds_list = []
            for x in relatedIds.split(','):
                relatedIds_list.append(x)
            print(relatedIds_list)
            if self.userId in relatedIds_list:
                print("安卓端id在平台指定的id范围内，符合条件")
                print("平台指定的id已经判断完毕")
                print("开始判断是否符合安卓端的id条件")
                # 判断安卓端的id是否符合条件
                if self.relatedIds == {}:
                    print("安卓端指定的id为空，符合条件，允许运行")
                    # 判断时间范围
                    if end_time and start_time:
                        print("开始进行时间范围判断")
                        if utils.is_current_time_in_range(start_time, end_time):
                            print("当前时间在任务执行范围内，允许发送消息")
                            # 发送给当前WebSocket客户端
                            try:
                                await self.send_message(data)
                                print("已经发送消息给安卓端")
                            except Exception as e:
                                print("发送消息失败")
                                print(e)
                        else:
                            print("当前时间不在任务执行范围内，不发送消息")
                    else:
                        print("没有设置时间范围，直接发送消息")
                        # 发送给当前WebSocket客户端
                        try:
                            await self.send_message(data)
                            print("已经发送消息给安卓端")
                        except Exception as e:
                            print("发送消息失败")
                            print(e)
                elif str(userId) in self.relatedIds["ids"]:
                    print("发送任务的id在安卓端指定的范围内，也符合条件")
                    # 判断时间范围
                    if end_time and start_time:
                        print("开始进行时间范围判断")
                        if utils.is_current_time_in_range(start_time, end_time):
                            print("当前时间在任务执行范围内，允许发送消息")
                            await self.send_message(data)
                        else:
                            print("当前时间不在任务执行范围内，不发送消息")
                    else:
                        print("没有设置时间范围，直接发送消息")
                        await self.send_message(data)
                else:
                    print("判断失败")
                    print(f'当前安卓关联id:{self.relatedIds["ids"]}')
                    print(f'类型为：{type(self.relatedIds["ids"])}')
            elif relatedIds_list == ['']:
                print("平台指定的id为空，也符合条件")
                # 判断时间范围
                if end_time and start_time:
                    print("开始进行时间范围判断")
                    if utils.is_current_time_in_range(start_time, end_time):
                        print("当前时间在任务执行范围内，允许发送消息")
                        await self.send_message(data)
                    else:
                        print("当前时间不在任务执行范围内，不发送消息")
                else:
                    print("没有设置时间范围，直接发送消息")
                    await self.send_message(data)
            else:
                print("不符合接收消息的条件")
                return
        else:
            print(f"类型是其他: {type(relatedIds)}")
       
        

        


