class DefaultAdminSite(LazyObject):

    def _setup(self):
        AdminSiteClass = import_string(apps.get_app_config('admin').default_site)
        self._wrapped = AdminSiteClass()

    def __repr__(self):
        return repr(self._wrapped)