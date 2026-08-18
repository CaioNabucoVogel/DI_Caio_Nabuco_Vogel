def add_routes(self, routes):
    self.settings.add_routes(routes)

    @routes.get('/users')
    async def get_users(request):
        if args.multi_user:
            return web.json_response({'storage': 'server', 'users': self.users})
        else:
            user_dir = self.get_request_user_filepath(request, None, create_dir=False)
            return web.json_response({'storage': 'server', 'migrated': os.path.exists(user_dir)})

    @routes.post('/users')
    async def post_users(request):
        body = await request.json()
        username = body['username']
        if username in self.users.values():
            return web.json_response({'error': 'Duplicate username.'}, status=400)
        try:
            user_id = self.add_user(username)
        except ValueError as e:
            return web.json_response({'error': str(e)}, status=400)
        return web.json_response(user_id)

    @routes.get('/userdata')
    async def listuserdata(request):
        """
            List user data files in a specified directory.

            This endpoint allows listing files in a user's data directory, with options for recursion,
            full file information, and path splitting.

            Query Parameters:
            - dir (required): The directory to list files from.
            - recurse (optional): If "true", recursively list files in subdirectories.
            - full_info (optional): If "true", return detailed file information (path, size, modified time).
            - split (optional): If "true", split file paths into components (only applies when full_info is false).

            Returns:
            - 400: If 'dir' parameter is missing.
            - 403: If the requested path is not allowed.
            - 404: If the requested directory does not exist.
            - 200: JSON response with the list of files or file information.

            The response format depends on the query parameters:
            - Default: List of relative file paths.
            - full_info=true: List of dictionaries with file details.
            - split=true (and full_info=false): List of lists, each containing path components.
            """
        directory = request.rel_url.query.get('dir', '')
        if not directory:
            return web.Response(status=400, text='Directory not provided')
        path = self.get_request_user_filepath(request, directory)
        if not path:
            return web.Response(status=403, text='Invalid directory')
        if not os.path.exists(path):
            return web.Response(status=404, text='Directory not found')
        recurse = request.rel_url.query.get('recurse', '').lower() == 'true'
        full_info = request.rel_url.query.get('full_info', '').lower() == 'true'
        split_path = request.rel_url.query.get('split', '').lower() == 'true'
        if recurse:
            pattern = os.path.join(glob.escape(path), '**', '*')
        else:
            pattern = os.path.join(glob.escape(path), '*')

        def process_full_path(full_path: str) -> FileInfo | str | list[str]:
            if full_info:
                return get_file_info(full_path, path)
            rel_path = os.path.relpath(full_path, path).replace(os.sep, '/')
            if split_path:
                return [rel_path] + rel_path.split('/')
            return rel_path
        results = [process_full_path(full_path) for full_path in glob.glob(pattern, recursive=recurse) if os.path.isfile(full_path)]
        return web.json_response(results)

    @routes.get('/v2/userdata')
    async def list_userdata_v2(request):
        """
            List files and directories in a user's data directory.

            This endpoint provides a structured listing of contents within a specified
            subdirectory of the user's data storage.

            Query Parameters:
            - path (optional): The relative path within the user's data directory
                               to list. Defaults to the root ('').

            Returns:
            - 400: If the requested path is invalid, outside the user's data directory, or is not a directory.
            - 404: If the requested path does not exist.
            - 403: If the user is invalid.
            - 500: If there is an error reading the directory contents.
            - 200: JSON response containing a list of file and directory objects.
                   Each object includes:
                   - name: The name of the file or directory.
                   - type: 'file' or 'directory'.
                   - path: The relative path from the user's data root.
                   - size (for files): The size in bytes.
                   - modified (for files): The last modified timestamp (Unix epoch).
            """
        requested_rel_path = request.rel_url.query.get('path', '')
        try:
            requested_rel_path = parse.unquote(requested_rel_path)
        except Exception as e:
            logging.warning(f'Failed to decode path parameter: {requested_rel_path}, Error: {e}')
            return web.Response(status=400, text='Invalid characters in path parameter')
        try:
            base_user_path = self.get_request_user_filepath(request, None, create_dir=False)
            if requested_rel_path:
                target_abs_path = self.get_request_user_filepath(request, requested_rel_path, create_dir=False)
            else:
                target_abs_path = base_user_path
        except KeyError as e:
            logging.warning(f'Access denied for user: {e}')
            return web.Response(status=403, text='Invalid user specified in request')
        if not target_abs_path:
            return web.Response(status=400, text='Invalid path requested')
        if not os.path.exists(target_abs_path):
            if target_abs_path == base_user_path:
                return web.json_response([])
            else:
                return web.Response(status=404, text='Requested path not found')
        if not os.path.isdir(target_abs_path):
            return web.Response(status=400, text='Requested path is not a directory')
        results = []
        try:
            for (root, dirs, files) in os.walk(target_abs_path, topdown=True):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    rel_path = os.path.relpath(dir_path, base_user_path).replace(os.sep, '/')
                    results.append({'name': dir_name, 'path': rel_path, 'type': 'directory'})
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(file_path, base_user_path).replace(os.sep, '/')
                    entry_info = {'name': file_name, 'path': rel_path, 'type': 'file'}
                    try:
                        stats = os.stat(file_path)
                        entry_info['size'] = stats.st_size
                        entry_info['modified'] = stats.st_mtime
                    except OSError as stat_error:
                        logging.warning(f'Could not stat file {file_path}: {stat_error}')
                        pass
                    results.append(entry_info)
        except OSError as e:
            logging.error(f'Error listing directory {target_abs_path}: {e}')
            return web.Response(status=500, text='Error reading directory contents')
        results.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        return web.json_response(results)

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

    @routes.get('/userdata/{file}')
    async def getuserdata(request):
        path = get_user_data_path(request, check_exists=True)
        if not isinstance(path, str):
            return path
        return web.FileResponse(path)

    @routes.post('/userdata/{file}')
    async def post_userdata(request):
        """
            Upload or update a user data file.

            This endpoint handles file uploads to a user's data directory, with options for
            controlling overwrite behavior and response format.

            Query Parameters:
            - overwrite (optional): If "false", prevents overwriting existing files. Defaults to "true".
            - full_info (optional): If "true", returns detailed file information (path, size, modified time).
                                  If "false", returns only the relative file path.

            Path Parameters:
            - file: The target file path (URL encoded if necessary).

            Returns:
            - 400: If 'file' parameter is missing.
            - 403: If the requested path is not allowed.
            - 409: If overwrite=false and the file already exists.
            - 200: JSON response with either:
                  - Full file information (if full_info=true)
                  - Relative file path (if full_info=false)

            The request body should contain the raw file content to be written.
            """
        path = get_user_data_path(request)
        if not isinstance(path, str):
            return path
        overwrite = request.query.get('overwrite', 'true') != 'false'
        full_info = request.query.get('full_info', 'false').lower() == 'true'
        if not overwrite and os.path.exists(path):
            return web.Response(status=409, text='File already exists')
        try:
            body = await request.read()
            with open(path, 'wb') as f:
                f.write(body)
        except OSError as e:
            logging.warning(f"Error saving file '{path}': {e}")
            return web.Response(status=400, reason='Invalid filename. Please avoid special characters like :\\/*?"<>|')
        user_path = self.get_request_user_filepath(request, None)
        if full_info:
            resp = get_file_info(path, user_path)
        else:
            resp = os.path.relpath(path, user_path)
        return web.json_response(resp)

    @routes.delete('/userdata/{file}')
    async def delete_userdata(request):
        path = get_user_data_path(request, check_exists=True)
        if not isinstance(path, str):
            return path
        os.remove(path)
        return web.Response(status=204)

    @routes.post('/userdata/{file}/move/{dest}')
    async def move_userdata(request):
        """
            Move or rename a user data file.

            This endpoint handles moving or renaming files within a user's data directory, with options for
            controlling overwrite behavior and response format.

            Path Parameters:
            - file: The source file path (URL encoded if necessary)
            - dest: The destination file path (URL encoded if necessary)

            Query Parameters:
            - overwrite (optional): If "false", prevents overwriting existing files. Defaults to "true".
            - full_info (optional): If "true", returns detailed file information (path, size, modified time).
                                  If "false", returns only the relative file path.

            Returns:
            - 400: If either 'file' or 'dest' parameter is missing
            - 403: If either requested path is not allowed
            - 404: If the source file does not exist
            - 409: If overwrite=false and the destination file already exists
            - 200: JSON response with either:
                  - Full file information (if full_info=true)
                  - Relative file path (if full_info=false)
            """
        source = get_user_data_path(request, check_exists=True)
        if not isinstance(source, str):
            return source
        dest = get_user_data_path(request, check_exists=False, param='dest')
        if not isinstance(dest, str):
            return dest
        overwrite = request.query.get('overwrite', 'true') != 'false'
        full_info = request.query.get('full_info', 'false').lower() == 'true'
        if not overwrite and os.path.exists(dest):
            return web.Response(status=409, text='File already exists')
        logging.info(f"moving '{source}' -> '{dest}'")
        shutil.move(source, dest)
        user_path = self.get_request_user_filepath(request, None)
        if full_info:
            resp = get_file_info(dest, user_path)
        else:
            resp = os.path.relpath(dest, user_path)
        return web.json_response(resp)