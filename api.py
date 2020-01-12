from flask import Flask, g
from ip_proxy.storage import RedisClient

__all__ = ['app']
app = Flask(__name__)

def get_coon():
    if not hasattr(g, 'redis'):
        g.redis = RedisClient()
    return g.redis

@app.route('/')
def index():
    return '<h2>welcome to Proxy Pool System<h2>'

@app.route('/random')
def get_proxy():
    """
    获取随机可用代理
    :return: 随机代理
    """
    coon = get_coon()
    return coon.random()

@app.route('/count')
def get_counts():
    """
    获取代理池总量
    :return: 代理池总量
    """
    conn = get_coon()
    return str(conn.count())

if __name__ == '__main__':
    app.run()