def remove_user(self):
    cmd = [self.module.get_bin_path('pw', True), 'userdel', '-n', self.name]
    if self.remove:
        cmd.append('-r')
    return self.execute_command(cmd)