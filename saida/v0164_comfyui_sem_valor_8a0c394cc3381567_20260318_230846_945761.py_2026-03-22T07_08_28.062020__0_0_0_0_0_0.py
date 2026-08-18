def __init__(self, *args: Any, ui: _UIOutput | dict=None, expand: dict=None, block_execution: str=None):
    self.args = args
    self.ui = ui
    self.expand = expand
    self.block_execution = block_execution