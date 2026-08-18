def _get_expected_relationship_type(self, element_name):
    elem_lower = element_name.lower()
    if elem_lower in self.ELEMENT_RELATIONSHIP_TYPES:
        return self.ELEMENT_RELATIONSHIP_TYPES[elem_lower]
    if elem_lower.endswith('id') and len(elem_lower) > 2:
        prefix = elem_lower[:-2]
        if prefix.endswith('master'):
            return prefix.lower()
        elif prefix.endswith('layout'):
            return prefix.lower()
        else:
            if prefix == 'sld':
                return 'slide'
            return prefix.lower()
    if elem_lower.endswith('reference') and len(elem_lower) > 9:
        prefix = elem_lower[:-9]
        return prefix.lower()
    return None