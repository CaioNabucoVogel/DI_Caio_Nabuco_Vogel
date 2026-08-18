def get_user_data_path(request, check_exists=False, param='file'):
    file = request.match_info.get(param, None)
    if not file:
        return web.Response(status=400)
    path = self.get_request_user_filepath(request, file)
    if not path:
        return web.Response(status=403)
    if check_exists and (not os.path.exists(path)):
        return web.Response(status=404)
    return path