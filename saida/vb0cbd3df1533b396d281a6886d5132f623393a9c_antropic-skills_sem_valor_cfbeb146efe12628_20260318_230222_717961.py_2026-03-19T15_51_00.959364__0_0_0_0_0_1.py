def _remove_ignorable_elements(self, root):
    elements_to_remove = []
    for elem in list(root):
        if not hasattr(elem, 'tag') or callable(elem.tag):
            continue
        tag_str = str(elem.tag)
        if tag_str.startswith('{'):
            ns = tag_str.split('}')[0][1:]
            if ns not in self.OOXML_NAMESPACES:
                elements_to_remove.append(elem)
                continue
        self._remove_ignorable_elements(elem)
    for elem in elements_to_remove:
        root.remove(elem)