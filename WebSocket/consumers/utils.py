"""
这个是工具类，用于处理http请求以及mq消息等
"""
import json
import os
import datetime

# 工具类
class Utils:
    def process_http_message(self, message):
        """
        从HTTP消息中提取指定字段
        
        Args:
            message: HTTP请求中的JSON数据
            
        Returns:
            dict: 包含提取字段的http_data字典
        """
        http_data = {}
        
        # 提取指定字段
        try:
            http_data['token'] = message.get('token', '')
            http_data['username'] = message.get('username', '')
            http_data['userId'] = message.get('userId', '')
            http_data['userCode'] = message.get('userCode', '')
            http_data['最低任务佣金'] = message.get('最低任务佣金', '')
            http_data['关联ID'] = message.get('关联ID', {})
        except Exception as e:
            print(f"处理HTTP消息时发生错误：{e}")
        
        return http_data

    def process_mq_message(self, userid):
        """
        根据userid从task_json文件夹中查找指定的userid文件夹，
        再获取最新的json文件，提取指定的字段并返回
        """
        latest_json_file_path = self.get_latest_json_file(userid)
        
        if not latest_json_file_path or not os.path.exists(latest_json_file_path):
            print(f"未找到用户{userid}的JSON文件")
            return {}
        
        try:
            with open(latest_json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 提取指定的字段
            mq_data = {}
            mq_data['task_code'] = data.get('task_code', '')
            mq_data['cost_trcoin'] = data.get('cost_trcoin', '')
            mq_data['script_url'] = data.get('script_url', '')
            mq_data['relatedIds'] = data.get('relatedIds', '')
            mq_data['userId'] = data.get('userId', '')
            mq_data['android_exe_status'] = data.get('android_exe_status', '')
            mq_data['start_time'] = data.get('start_time', '')
            # mq_data['content'] = data.get('content', {})
            return mq_data
        except Exception as e:
            print(f"读取JSON文件时发生错误：{e}")
            return {}

    def get_latest_json_file(self, userid):
        """
        根据userid从task_json文件夹中查找指定的userid文件夹，
        再获取最新的json文件，并返回文件路径
        """
        base_path = f"task_json/userid_{userid}"
        latest_json_file_path = ""
        # 获取当前文件夹下最新的json文件
        json_files = []
        for filename in os.listdir(base_path):
            if filename.endswith('.json'):
                json_files.append(filename)
        
        if json_files:
            # 显示所有文件信息，用于调试
            print("=== 文件信息 ===")
            for f in json_files:
                print(f"文件：{f}")
            
            # 按文件名排序（文件名包含时间信息，按字典序排序即可）
            json_files.sort()  # 按文件名升序排列
            print(f"\n按文件名排序（从旧到新）：")
            for f in json_files:
                print(f"  {f}")
            
            # 获取最新的文件（文件名最大的）
            latest_file = max(json_files)  # 直接按文件名排序，获取最大的
            latest_json_file_path = os.path.join(base_path, latest_file)
            print(f"\n找到最新文件：{latest_json_file_path}")
            print("==================")
        else:
            print(f"用户{userid}的文件夹中没有找到JSON文件")
            latest_json_file_path = ""
        
        return latest_json_file_path

    def get_current_timestamp(self):
        """
        获取当前时间戳
        
        Returns:
            str: 格式化的时间戳字符串
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")



