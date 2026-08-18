def user_info(self):
    info = super(SunOS, self).user_info()
    if info:
        info += self._user_attr_info()
    return info