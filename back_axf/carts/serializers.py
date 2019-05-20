
from rest_framework import serializers

from carts.models import Cart
from goods.serializers import GoodsSerializer


class CartSerializer(serializers.ModelSerializer):
    # 序列化 c_goods字段，解决图片显示问题
    c_goods = GoodsSerializer()

    class Meta:
        model = Cart
        fields = '__all__'

















