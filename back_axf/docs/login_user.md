### 登录接口

#### 请求地址：/api/user/auth/login/

#### 请求方式：POST

####　请求参数：
    u_username 登录账号 string 必填
    u_password 登录密码 string 必填
    
#### 响应

##### 1.响应成功
    {
        code：200，
        msg：‘请求成功’，
        data：{
            token：sdfadfadsfasdf,
        }
    }
        
##### 2.响应失败
    {
        ‘code’：1004，
        ‘msg’： ‘登录’
    }
    
    
    
#### 响应参数
    code 状态吗 int
    msg  响应信息 string
    token 登录标识符 string