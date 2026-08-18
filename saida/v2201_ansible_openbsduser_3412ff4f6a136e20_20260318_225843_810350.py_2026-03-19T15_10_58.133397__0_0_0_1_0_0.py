def remove_user_userdel(self):
    cmd = [self.module.get_bin_path('userdel', True)]
    if self.remove:
        cmd.append('-r')
    cmd.append(self.name)
    return self.execute_command(cmd)