class ClusterConfig:
    def __init__(self,meta={}):
        self.servers=meta
    def add_server(self, server_id, server_address):
        self.servers[server_id] = server_address

    def remove_server(self, server_id):
        if server_id in self.servers:
            del self.servers[server_id]
    def get_server_address(self, server_id):
        return self.servers.get(server_id)