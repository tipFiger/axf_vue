from functools import wraps

from django.core.cache import cache

from user.models import AXFUser
from utils import errors


def is_login(func):
    @wraps(func)
    def check(request,*args,**kwargs):
        # 获取前端传递的token，提取数据数据库的token，校验
        token = request.query_params.get('token') if request.query_params.get('token') else request.data.get('token')
        user_id = cache.get(token)
        if not user_id:
            res = {
                'code': 1007,
                'msg': '用户认证失败，无法操作'
            }
            raise errors.ParamsException(res)
        if user_id:
            user = AXFUser.objects.filter(pk=user_id).first()
            return user, token
        return func(request,*args,**kwargs)
    return check