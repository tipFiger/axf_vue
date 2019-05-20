from django.core.cache import cache

from django.shortcuts import render

from rest_framework import mixins, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from carts.models import Cart
from carts.serializers import CartSerializer
from utils.UserAuthentication import UserAuth
# from utils.functions import is_login


class CartView(viewsets.GenericViewSet,
               mixins.ListModelMixin,
               mixins.UpdateModelMixin):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    # 一、认证的方式
    authentication_classes = (UserAuth,)

    # 购物车列表页面
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # 当前登录系统用户的购物车信息 c_user  获取数据-过滤-序列化校验-数据传给前端
        queryset = queryset.filter(c_user=request.user)
        serializer = self.get_serializer(queryset, many=True)

        # 计算总价
        queryset = queryset.filter(c_is_select=1).all()
        total_price = 0
        for cart in queryset:
            total_price += cart.c_goods.price*cart.c_goods_num

        res = {
            'carts':serializer.data,  # 传给前端
            'total_price': total_price
        }
        return Response(res)



    @list_route(methods=['POST'])
    def add_cart(self, request, *args, **kwargs):
        # 思路：登录状态和未登录状态
        # 1、登录信息判断，cache的使用，获取前端传回的token和redis中的token
        # token = self.request.data.get('token')
        goodsid = request.data.get('goodsid')
        # user_id = cache.get(token)
        cart = Cart.objects.filter(c_user=request.user,c_goods_id=goodsid).first()
        if not cart:
            # 3、如果当前登录用户没有店家该商品，则创建购物车的信息
            Cart.objects.create(c_user=request.user,c_goods_id=goodsid)
        else:
            # 2、当前登录用户添加商品，对应商品加1
            cart.c_goods_num += 1
            cart.save()
        res = {
            'code':200,
            'msg':'添加成功'
        }

        # 4、视登录状态，直接返回相应响应状态
        return Response(res)

    @list_route(methods=['POST'])
    def sub_cart(self, request, *args, **kwargs):
        # 获取当前用户，获取对应商品，筛选，判断数量
        user = request.user
        goodsid = request.data.get('goodsid')
        carts = Cart.objects.filter(c_user=user, c_goods_id=goodsid).first()
        res = {
            'code': 200,
            'msg': '操作商品成功'
        }

        # 购物车中没有该商品的信息
        if not carts:
            res = {
                'code': 1008,
                'msg': '未添加购物车'
            }
        # 有商品且数量大于1
        if carts.c_goods_num > 1:
            # 商品数-1
            carts.c_goods_num = 1
            carts.save()
            # res = {
            #     'code': 200,
            #     'msg': '操作商品成功'
            # }

        else:
            carts.delete()

            # res = {
            #     'code': 200,
            #     'msg': '操作商品成功'
            # }

        # 4、视登录状态，直接返回相应响应状态
        return Response(res)

    # 二、list_route路由装饰器的方法
    # @list_route(methods=['POST'])
    # @is_login
    # # 添加购物车功能
    # def add_cart(self,request,*args,**kwargs):
    #     # 思路：登录状态和未登录状态
    #     # 1、登录信息判断，cache的使用，获取前端传回的token和redis中的token
    #     token = self.request.data.get('token')
    #     goodsid = request.data.get('goodsid')
    #     user_id = cache.get(token)
    #     if user_id:
    #
    #         cart = Cart.objects.filter(c_user_id=user_id,c_goods_id=goodsid).first()
    #         if not cart:
    #             # 3、如果当前登录用户没有店家该商品，则创建购物车的信息
    #             Cart.objects.create(c_user_id=user_id,c_goods_id=goodsid)
    #         else:
    #             # 2、当前登录用户添加商品，对应商品加1
    #             cart.c_goods_num += 1
    #             cart.save()
    #         res = {
    #             'code':200,
    #             'msg':'添加成功'
    #         }
    #
    #     else:
    #         res = {
    #             'code': 1007,
    #             'msg': '账号未登录'
    #         }
    #     # 4、视登录状态，直接返回相应响应状态
    #     return Response(res)


    #
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # 取反
        instance.c_is_select = not instance.c_is_select
        instance.save()

        res = {
            'code': 200,
            'msg':'修改成功'
        }
        return Response(res)


    #
    @list_route(methods=['PATCH'])
    def change_select(self,request,*args,**kwargs):
        # 修改x
        user = request.user
        Cart.objects.filter(c_user=user).update(c_is_select=1)

        res = {
            'code': 200,
            'msg': '请求成功'
        }

        return Response(res)




