def set(self, node_id, value):
    self.timestamps[self.cache_key_set.get_data_key(node_id)] = time.time()
    super().set(node_id, value)