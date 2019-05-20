

from rest_framework import viewsets, mixins
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django.core.cache import cache

from user.models import AXFUser
from user.serializers import UserSerializer, UserRegisterSerializers, UserLoginSerializers
from utils import errors


# 单个资源查询的方法
class UserView(viewsets.GenericViewSet,
               mixins.ListModelMixin):
    queryset = AXFUser.objects.all()
    serializer_class = UserSerializer

    # 重构list方法，用于返回登录用户信息
    def list(self, request, *args, **kwargs):
        # 1先获取前端请求中传递的token
        token = request.query_params.get('token')
        # request._request.get


        # 2通过token 从redis 中取用户的id值
        user_id = cache.get(token)


        # 3序列化用户对象
        user = AXFUser.objects.filter(id=user_id).first()
        serializer = self.get_serializer(user)
        # TODO: 订单的待付款和待收货功能后续完成
        res = {
            # 当前登录用户的信息
            'user_info': serializer.data,
            # 订单未支付数量
            'order_not_pay_num': 0,
            # 订单未发送数量
            'orders_not_send_num': 0,
        }

        return Response(res)



    # 注册接口
    @list_route(methods=['POST'], serializer_class=UserRegisterSerializers)
    def register(self, request, *args, **kwargs):
        # 装饰器添加register路由：  /api/user/auth   /register/
        serializer = self.get_serializer(data=request.data)
        result = serializer.is_valid(raise_exception=False)
        if not result:
            raise errors.ParamsException({'code': 1003, 'msg': '参数校验失败', 'data': serializer.errors})

        # 保存用户信息，传的是校验过后的值
        user = serializer.register_user(serializer.data)
        # 返回的结构  res的是data的结果
        res = {'user_id': user.id}
        return Response(res)

    # 登录接口
    @list_route(methods=['POST'], serializer_class=UserLoginSerializers)
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        result = serializer.is_valid(raise_exception=False)
        if not result:
            raise errors.ParamsException({'code':1006, 'msg':'校验登录参数有误'})


        # 登录用户
        token = serializer.login_user(serializer.data)

        # 登录返回结构  {'code':200, 'msg':'',data:{token:token值}}
        res = {'token':token}
        return Response(res)




