def create_arg(self, a: object) -> fx.node.Node:
    if isinstance(a, torch.nn.Parameter):
        for (n, p) in self.root.named_parameters():
            if a is p:
                return self.create_node('get_attr', n, (), {})
        qualname = self.get_fresh_qualname('_param_constant')
        setattr(self.root, qualname, a)
        return self.create_node('get_attr', qualname, (), {})
    elif isinstance(a, py_sym_types):
        assert a.node.constant is not None
        return a.node.constant
    return super().create_arg(a)