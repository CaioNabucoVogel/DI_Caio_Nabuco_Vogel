def expand(self, batch_shape: _size, _instance: Optional['Pareto']=None) -> 'Pareto':
    new = self._get_checked_instance(Pareto, _instance)
    new.scale = self.scale.expand(batch_shape)
    new.alpha = self.alpha.expand(batch_shape)
    return super().expand(batch_shape, _instance=new)