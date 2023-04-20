from rediscluster import RedisCluster as Redis

if __name__ == '__main__':
    rc = Redis(host='192.168.0.12', port=8000,
               decode_responses=True, socket_timeout=2)

    rc.set('foo', 'bar')
    value = rc.get('foo')
    print(value)
