# 导入必要的库
from django.http import JsonResponse
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
import json

# http请求转发接口，用于将http请求转发给autojs
@csrf_exempt
def forward_to_specific_websocket(request, client_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        channel_layer = get_channel_layer()
        # 获取特定客户端的channel_name
        target_channel = cache.get(f"ws_{client_id}")
        if target_channel:
            async_to_sync(channel_layer.send)(
                target_channel,  # 直接发送给特定channel
                {
                    'type': 'http_message',
                    'message': data
                }
            )
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Client not found'})
    elif request.method == 'GET':
        return JsonResponse({'status': 'success', 'message': 'GET请求成功'})
