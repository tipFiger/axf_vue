import json
from django.shortcuts import render

# 多资源查询https://www.django-rest-framework.org/tutorial/3-class-based-views/

# def home():
#     return JsonResponse()
from rest_framework import viewsets, mixins

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django_redis import get_redis_connection

from rest_framework.views import APIView
# 函数视图
from goods.filters import GoodFilter
from goods.models import MainWheel, MainNav, MainMustBuy, MainShop, MainShow, FoodType, Goods
from goods.serializers import MainWheelSerializer, MainNavSerializer, MainMustBuySerializer, MainShopSerializer, \
    MainShowSerializer, FoodTypeSerializer, GoodsSerializer


# 类视图  官网的写法
class Home(APIView):
    def get(self, request):
        main_wheels = MainWheel.objects.all()
        main_navs = MainNav.objects.all()
        main_mustbuy = MainMustBuy.objects.all()
        main_shops = MainShop.objects.all()
        main_shows = MainShow.objects.all()

        # 进行序列化serializer

        res = {
            'main_wheels': MainWheelSerializer(main_wheels, many=True).data,
            'main_navs': MainNavSerializer(main_navs, many=True).data,
            'main_mustbuy': MainMustBuySerializer(main_mustbuy, many=True).data,
            'main_shops': MainShopSerializer(main_shops, many=True).data,
            'main_shows': MainShowSerializer(main_shows, many=True).data,

        }

        return Response(res)


@api_view(['GET'])
def home(request):
    # 优化，redis缓存， 用hash的数据结构
    # hash ： goods   main_wheels   MainWheelSerializer(main_wheels, many=True).data
    # 获取redis原声对象from django_redis import get_redis_connection
    # 使用redis  创建连接对象redis.Redis(port,host,password)
    conn = get_redis_connection()
    # 取值
    if not conn.hget('goods', ' main_wheels'):
        # 获取数据
        mainwheels = MainWheel.objects.all()

        # 添加数据
        value = MainWheelSerializer(mainwheels, many=True).data

        # 字典转换json
        value = json.dumps(value)
        conn.hset('goods', 'main_wheels', value)
    redis_main_wheels = json.loads(conn.hget('goods', 'main_wheels').decode('utf8'))

    if not conn.hget('goods', 'main_navs'):
        # 获取数据
        main_navs = MainNav.objects.all()
        # 添加数据
        value = MainNavSerializer(main_navs, many=True).data
        value = json.dumps(value)
        conn.hset('goods', 'main_navs', value)
    redis_main_navs = json.loads(conn.hget('goods', 'main_navs').decode('utf8'))

    if not conn.hget('goods', 'main_mustbuy'):
        # 获取数据
        main_mustbuy = MainMustBuy.objects.all()
        # 添加数据
        value = MainMustBuySerializer(main_mustbuy, many=True).data
        value = json.dumps(value)
        conn.hset('goods', 'main_mustbuy', value)
    redis_main_mustbuy = json.loads(conn.hget('goods', 'main_mustbuy').decode('utf8'))

    if not conn.hget('goods', 'main_shops'):
        # 获取数据
        main_shops = MainShop.objects.all()
        # 添加数据
        value = MainShopSerializer(main_shops, many=True).data
        value = json.dumps(value)
        conn.hset('goods', 'main_shops', value)
    redis_main_shops = json.loads(conn.hget('goods', 'main_shops').decode('utf8'))

    if not conn.hget('goods', 'main_shows'):
        # 获取数据
        main_shows = MainShow.objects.all()
        # 添加数据
        value = MainShowSerializer(main_shows, many=True).data
        value = json.dumps(value)
        conn.hset('goods', 'main_shows', value)
    redis_main_shows = json.loads(conn.hget('goods', 'main_shows').decode('utf8'))

    # 获取资源
    # main_wheels = MainWheel.objects.all()
    # main_navs = MainNav.objects.all()
    # main_mustbuy = MainMustBuy.objects.all()
    # main_shops = MainShop.objects.all()
    # main_shows = MainShow.objects.all()

    # 进行序列化serializer

    res = {
        'main_wheels': redis_main_wheels,  # MainWheelSerializer(main_wheels, many=True).data,
        'main_navs': redis_main_navs,  # MainNavSerializer(main_navs, many=True).data,
        'main_mustbuy': redis_main_mustbuy,  # MainMustBuySerializer(main_mustbuy, many=True).data,
        'main_shops': redis_main_shops,  # MainShopSerializer(main_shops, many=True).data,
        'main_shows': redis_main_shows,  # MainShowSerializer(main_shows, many=True).data,

    }

    return Response(res)


class FoodTypeView(viewsets.GenericViewSet,
                   mixins.ListModelMixin):
    queryset = FoodType.objects.all()
    serializer_class = FoodTypeSerializer

    # 获取分类的响应结果
    # res = {
    #     'code': 1007,
    #     'msg': '展示成功',
    #     'data':{
    #         'queryset':queryset
    #     }
    # }


class MarketView(viewsets.GenericViewSet,
                 mixins.ListModelMixin):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    filter_class = GoodFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        typeid = self.request.query_params.get('typeid')
        food_type = FoodType.objects.filter(typeid=typeid).first()
        # 第一种方式：for循环取子分类的信息
        child_list = []
        for childname in food_type.childtypenames.split('#'):
            data = {
                'child_name': childname.split(':')[0],
                'child_value': childname.split(':')[1]
            }
            child_list.append(data)

        # 第二种方式  列表推导式
        # foodtype_childname_list = [{
        #         'child_name':childname.split(':')[0],
        #         'child_value':childname.split(':')[1]
        #     } for childnames in food_type.childtypenames.split]

        foodtype_childname_list = [
            {'child_value': 0, 'child_name': '全部分类'},
            {'child_value': 103534, 'child_name': '进口水果'},
            {'child_value': 103533, 'child_name': '国产水果'},

        ]

        # 排序
        order_rule_list = [
            {'order_name': '综合排序', 'order_value': 0},
            {'order_name': '价格升序', 'order_value': 1},
            {'order_name': '价格降序', 'order_value': 2},
            {'order_name': '销量升序', 'order_value': 3},
            {'order_name': '销量降序', 'order_value': 4},
        ]

        res = {
            'goods_list': serializer.data,
            'order_rule_list': order_rule_list,
            'foodtype_childname_list': foodtype_childname_list,

        }
        return Response(res)
