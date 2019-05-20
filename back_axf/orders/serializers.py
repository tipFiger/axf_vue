
from rest_framework import serializers

from goods.serializers import GoodsSerializer
from orders.models import Order, OrderGoods


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'

    # 二 、 使用to_representation
    def to_representation(self, instance):
        # instance 就是订单对象
        # Python2 super(OrderSerializer, self).to_representation(instance)
        data = super().to_representation(instance)
        order_goods = instance.ordergoods_set.all()
        data['order_goods_info'] = OrderGoodsSerializer(order_goods, many=True).data

        return data


class OrderGoodsSerializer(serializers.ModelSerializer):

    o_goods = GoodsSerializer()

    class Meta:
        model = OrderGoods
        fields = '__all__'





