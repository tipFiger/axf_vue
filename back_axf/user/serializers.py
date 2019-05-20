import uuid

from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache
from rest_framework import serializers

from user.models import AXFUser


# 用户序列化，序列化所有字段和用户模型，父类ModelSerializer
from utils import errors


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AXFUser
        fields = '__all__'


# 注册序列化,起到校验字段的作用，父类Serializer
class UserRegisterSerializers(serializers.Serializer):
    u_username = serializers.CharField(required=True, max_length=10, min_length=3,
                                       error_messages={'required': '注册账号必填','blank': '账号不能为空', 'max_length': '注册账号不超过10',
                                                       'min_length': '注册账号不少于3字符'})
    u_password = serializers.CharField(required=True, max_length=10, min_length=5,
                                       error_messages={'required': '注册密码必填','blank': '注册密码不能为空', 'max_length': '注册账号不超过10',
                                                       'min_length': '注册账号不少于5字符'})
    u_password2 = serializers.CharField(required=True, max_length=10, min_length=5,
                                        error_messages={'required': '注册确认必填','blank': '确认不能为空', 'max_length': '注册账号不超过10',
                                                        'min_length': '注册账号不少于5字符'})
    u_email = serializers.EmailField(required=True, error_messages={'required': '邮箱必填','blank': '注册邮箱不能为空',})


    def validate(self, attrs):
        # 账号是否存在
        username = attrs.get('u_username')
        #                      数据库的名
        user = AXFUser.objects.filter(u_username=username).first()
        if user:
            raise errors.ParamsException({'code':1001,'msg':'注册账号已存在，请重新输入'})


        # 密码是否一致
        pwd1 = attrs.get('u_password')
        pwd2 = attrs.get('u_password2')
        if pwd1 != pwd2:
            raise errors.ParamsException({'code':1002,'msg':'密码不一致，请确认相同的密码'})
        # 邮箱(字段验证Emailfield、正则Charfield都要会),判断邮箱是否是否存在
        # email = attrs.get('u_email')
        # if email:
        #     raise errors.ParamsException({'code':1003,'msg':'邮箱已存在已存在，请重新输入'})


        # 以上有问题抛异常
        return attrs


    # 注册，保存用户信息
    def register_user(self, validate_attr):
        username = validate_attr.get('u_username')
        password = make_password(validate_attr.get('u_password'))
        email = validate_attr.get('u_email')
        user = AXFUser.objects.create(u_username=username,
                               u_password=password,
                               u_email=email)


        return user



class UserLoginSerializers(serializers.Serializer):
    u_username = serializers.CharField(required=True, max_length=10, min_length=3,
                                       error_messages={'required': '登录账号必填', 'blank': '登录账号不能为空',
                                                       'max_length': '登录账号不超过10',
                                                       'min_length': '注册账号不少于3字符'})
    u_password = serializers.CharField(required=True, max_length=10, min_length=5,
                                       error_messages={'required': '登录密码必填', 'blank': '登录密码不能为空',
                                                       'max_length': '登录账号不超过10',
                                                       'min_length': '注册账号不少于5字符'})

    def validate(self, attrs):
        #判断账号是否存在，首先获取账号
        username = attrs.get('u_username')
        password = attrs.get('u_password')
        user = AXFUser.objects.filter(u_username=username).first()

        if not user:
            raise errors.ParamsException({'code':1004, 'msg':'账号不存在，请注册后登录'})

        # 判断密码是否一致
        if not check_password(password, user.u_password):
            raise errors.ParamsException({'code':1005, 'msg':'登录密码错误'})

        return attrs

    # 登录方法，返回token参数给前端，且保存token到redis
    def login_user(self, validate_attr):
        token = uuid.uuid4().hex
        user = AXFUser.objects.filter(u_username=validate_attr.get('u_username')).first()

        # 后端redis保存数据
        cache.set(token,user.id, timeout=86400)


        return token   # 返回给前端


