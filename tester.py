from ip_proxy.setting import *
from ip_proxy.storage import RedisClient
import asyncio
import aiohttp
import uvloop
import time

try:
    from aiohttp import ClientError
except:
    from aiohttp import ClientProxyConnectionError

class Tester(object):
    def __init__(self):
        self.redis = RedisClient()

    async def test_single_proxy(self, proxy):
        """
        测试单个代理
        :param proxy:代理
        :return: None
        """
        conn = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('正在测试', proxy)
                async with session.get(TEST_URL, proxy=real_proxy, timeout=15) as resonse:
                    if resonse.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('代理可用',proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('请求响应码不合法', proxy)
            except (ClientError, aiohttp.ClientProxyConnectionError, asyncio.TimeoutError, AttributeError):
                self.redis.decrease(proxy)
                print('代理请求失败', proxy)

    def run(self):
        """
        测试主函数
        :return: None
        """
        print('检测器开始运行')
        try:
            proxies = self.redis.all()
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            loop = asyncio.get_event_loop()
            #批量测试
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i: i+BATCH_TEST_SIZE]
                tasks = [asyncio.ensure_future(self.test_single_proxy(proxy)) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)
        except Exception as e:
            print("检测器发生错误", e)

if __name__ == "__main__":
    tester = Tester()
    tester.run()
