def get_ordered_ancestry_internal(self, dynprompt, node_id, ancestors, order_mapping):
    if not dynprompt.has_node(node_id):
        return
    inputs = dynprompt.get_node(node_id)['inputs']
    input_keys = sorted(inputs.keys())
    for key in input_keys:
        if is_link(inputs[key]):
            ancestor_id = inputs[key][0]
            if ancestor_id not in order_mapping:
                ancestors.append(ancestor_id)
                order_mapping[ancestor_id] = len(ancestors) - 1
                self.get_ordered_ancestry_internal(dynprompt, ancestor_id, ancestors, order_mapping)