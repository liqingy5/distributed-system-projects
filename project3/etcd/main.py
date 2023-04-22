import etcd3

etcd = etcd3.client(host='127.0.0.1', port=50051)
etcd.put('foo', 'bar')
print(etcd.get('foo')[0].decode('utf-8'))
