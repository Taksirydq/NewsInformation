# -*- coding:utf-8 -*-

from info.lib.yuntongxun.CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8aaf070866196530016623366b8706d5'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = 'fed35b19fa5748f682f03337799f8825'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8aaf070866196530016623366bed06dc'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'app.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'


# 云通讯官方提供的发送短信代码实例
# # 发送模板短信
# # @param to 手机号码
# # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# # @param $tempId 模板Id
#
# def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK

#      验证用户身份（每次发送短信验证都会验证）
#     rest = REST(serverIP, serverPort, softVersion)
#     rest.setAccount(accountSid, accountToken)
#     rest.setAppId(appId)
#     rest = REST(serverIP, serverPort, softVersion)
#     rest.setAccount(accountSid, accountToken)
#     rest.setAppId(appId)
#      发送短信验证码
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     for k, v in result.iteritems():
#
#         if k == 'templateSMS':
#             for k, s in v.iteritems():
#                 print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)


# c = CCP() ---> if判断能够通过，去进行用户鉴定权限操作
# c1 = CCP() --> if判断不会通过，直接将对象返回，不会再次进行用户鉴定权限处理
class CCP(object):
    """发送短信的辅助类"""

    def __new__(cls, *args, **kwargs):
        # 判断是否存在类属性_instance，_instance是类CCP的唯一对象，即单例
        if not hasattr(CCP, "_instance"):
            # 将耗时的网络请求封装到单利中，只会第一次初始化对象的时候才来验证，后面就不会来了
            # 调用父类的__new__创建对象
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance.rest = REST(_serverIP, _serverPort, _softVersion)
            cls._instance.rest.setAccount(_accountSid, _accountToken)
            cls._instance.rest.setAppId(_appId)
            # 返回对象
        return cls._instance

    def send_template_sms(self, to, datas, temp_id):
        """发送模板短信"""
        # @param to 手机号码
        # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
        # @param temp_id 模板Id
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        # 如果云通讯发送短信成功，返回的字典数据result中statuCode字段的值为"000000"
        if result.get("statusCode") == "000000":
            # 返回0 表示发送短信成功
            return 0
        else:
            # 返回-1 表示发送失败
            return -1


if __name__ == '__main__':
    ccp = CCP()
    # 注意： 测试的短信模板编号为1
    ccp.send_template_sms('18620593492', ['1234', 5], 1)
