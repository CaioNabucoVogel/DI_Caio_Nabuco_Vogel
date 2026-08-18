@staticmethod
def fix_proxy_path_params(path_params):
    proxy_path_param_value = path_params.get('proxy+')
    if not proxy_path_param_value:
        return
    del path_params['proxy+']
    path_params['proxy'] = proxy_path_param_value