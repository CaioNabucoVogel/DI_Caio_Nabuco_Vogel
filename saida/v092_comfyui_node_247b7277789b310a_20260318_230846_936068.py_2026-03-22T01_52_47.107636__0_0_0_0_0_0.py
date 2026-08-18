class Node:

    def __init__(self, id, class_type, inputs):
        self.id = id
        self.class_type = class_type
        self.inputs = inputs
        self.override_display_id = None

    def out(self, index):
        return [self.id, index]

    def set_input(self, key, value):
        if value is None:
            if key in self.inputs:
                del self.inputs[key]
        else:
            self.inputs[key] = value

    def get_input(self, key):
        return self.inputs.get(key)

    def set_override_display_id(self, override_display_id):
        self.override_display_id = override_display_id

    def serialize(self):
        serialized = {'class_type': self.class_type, 'inputs': self.inputs}
        if self.override_display_id is not None:
            serialized['override_display_id'] = self.override_display_id
        return serialized