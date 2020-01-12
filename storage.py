import redis
from ip_proxy.setting import *
from random import choice
from ip_proxy.error import PoolEmptyError
import re


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis 密码
        """
        self.db = redis.Redis(host=host, port=port, password=password, decode_responses=True)

    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not re.match("\d+\.\d+\.\d+\.\d+\:\d+",proxy):
            print("代理不符合规范",proxy,"丢弃")
            return
        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, {proxy: score})

    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果最高分数代理不存在，则按排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            try:
                if len(result):
                    return choice(result)
                else:
                    raise PoolEmptyError
            except PoolEmptyError as e:
                print(e)

    def decrease(self, proxy: str):
        """
        代理值减少一分，分数小于最小值则代理删除
        :type proxy: str
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print("代理：", proxy, '当前分数：', score, "减1")
            assert isinstance(proxy, str)
            return self.db.zincrby(REDIS_KEY, -1, proxy)
        else:
            print("代理", proxy, "当前分数", score, "移除")
            assert isinstance(proxy, str)
            return self.db.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        """
        判断是否存在
        :param proxy:代理
        :return: 是否存在
        """
        return not self.db.zscore(REDIS_KEY, proxy) is None

    def max(self, proxy):
        """
        讲代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        print("代理", proxy, "可用", MAX_SCORE)
        return self.db.zadd(REDIS_KEY, {proxy: MAX_SCORE})

    def count(self):
        """
        获取数量
        :return:数量
        """
        return self.db.zcard(REDIS_KEY)

    def all(self):
        """
        获取全部代理
        :return: 全部代理列表
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    def batch(self, start, stop):
        """
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        return self.db.zrevrange(REDIS_KEY, start, stop - 1)

    def test_rm(self, proxy):
        """
        删除测试数据
        :return: 删除结果
        """
        return self.db.zrem(REDIS_KEY, proxy)
    
if __name__ == "__main__":

    a = RedisClient()
    a.add("10.10.10.10:99")
    print(a.random())
    print(a.exists("10.10.10.10:99"))
    print(a.count())
    #print(a.all())
    #print(a.batch(680, 688))
    print(a.decrease("10.10.10.10:99"))
    print(a.random())
    print(a.decrease("10.10.10.10:99"))
    a.test_rm("10.10.10.10:99")
    print(a.exists("10.10.10.10:99"))
