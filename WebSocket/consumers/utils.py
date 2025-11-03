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
            # 检查 message 是否为字典类型
            if not isinstance(message, dict):
                print(f"错误：process_http_message 接收到的 message 不是字典类型，实际类型：{type(message)}")
                print(f"message 内容：{message}")
                return http_data
            
            http_data['token'] = message.get('token', '')
            http_data['username'] = message.get('username', '')
            http_data['userId'] = message.get('userId', '')
            http_data['userCode'] = message.get('userCode', '')
            http_data['最低任务佣金'] = message.get('最低任务佣金', '')
            http_data['关联ID'] = message.get('关联ID', {})
            
            # 调试信息：打印提取的数据
            print(f"成功提取 http_data：{http_data}")
        except Exception as e:
            print(f"处理HTTP消息时发生错误：{e}")
            import traceback
            traceback.print_exc()
        
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
            mq_data['start_time'] = data.get('start_time', '') # 示例："start_time": "2025-10-14 13:10:20",
            mq_data['end_time'] = data.get('end_time','') # 示例 "end_time": "2025-10-16 00:00:00"
            mq_data['android_exe_status'] = data.get('android_exe_status','')
            mq_data['content'] = data.get('content', {}) # 脚本参数
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

    def is_current_time_in_range(self, start_time_str, end_time_str):
        """
        判断当前时间是否在指定时间范围内
        
        Args:
            start_time_str: 开始时间字符串，格式："2025-10-14 13:10:20"
            end_time_str: 结束时间字符串，格式："2025-10-16 00:00:00"
        
        Returns:
            bool: 当前时间在范围内返回True，否则返回False
        """
        try:
            # 获取当前时间
            current_time = datetime.datetime.now()
            
            # 解析时间字符串
            start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
            
            # 判断当前时间是否在范围内
            is_in_range = start_time <= current_time <= end_time
            
            print(f"时间判断结果:")
            print(f"  当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  是否在范围内: {is_in_range}")
            
            return is_in_range
            
        except Exception as e:
            print(f"时间判断出错: {e}")
            return False



