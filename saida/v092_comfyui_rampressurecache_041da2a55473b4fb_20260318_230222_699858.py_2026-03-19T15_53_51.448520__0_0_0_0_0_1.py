def get(self, node_id):
    self.timestamps[self.cache_key_set.get_data_key(node_id)] = time.time()
    return super().get(node_id)