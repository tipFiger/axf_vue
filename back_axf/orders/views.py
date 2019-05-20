
from rest_framework import viewsets,mixins
from rest_framework.response import Response

from carts.models import Cart
from orders.filters import OrderFilter
from orders.models import Order, OrderGoods
from orders.serializers import OrderSerializer, OrderGoodsSerializer
from utils.UserAuthentication import UserAuth


class OrderView(viewsets.GenericViewSet,
                mixins.ListModelMixin,
                mixins.CreateModelMixin):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # 认证用户
    authentication_classes = (UserAuth,)
    # 过滤
    filter_class = OrderFilter

    # 一、重构list方法：为什么重构？ ,重构的内容 二 、 1serializers.py中使用to_representation
    # list方法的返回结构{code：200， msg：‘’ ， data：[{订单， order_goods_info}， {}]}
    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     queryset = queryset.filter(o_user=request.user)
    #     # 序列化
    #     serializer = self.get_serializer(queryset, many=True)
    #     for order in serializer.data:
    #         order_goods = OrderGoods.objects.filter(o_order=order['id']).all()
    #         order['order_goods_info'] = OrderGoodsSerializer(order_goods, many=True).data

        # return Response(serializer.data)

    # 二、2
    def get_queryset(self):
        return self.queryset.filter(o_user=self.request.user)

    def create(self, request, *args, **kwargs):
        # 创建订单和订单详情表内容,  用户request.user
        carts = Cart.objects.filter(c_is_select=1,c_user=request.user).all()
        if carts:
            # 计算总价
            total_price = 0
            for cart in carts:
                total_price += cart.c_goods.price * cart.c_goods_num
            # 创建订单
            order = Order.objects.create(o_user=request.user, o_price=total_price)

            # 创建订单详情
            for cart in carts:
                OrderGoods.objects.create(o_order=order,
                                          o_goods=cart.c_goods,
                                          o_goods_num=cart.c_goods_num)

                # 删除购物车的商品信息
                cart.delete()

            res = {
                'code': 200,
                'msg': '下单成功'
            }
            return Response(res)

        res = {
            'code': 1009,
            'msg': '请先添加商品'
        }

        return Response(res)




