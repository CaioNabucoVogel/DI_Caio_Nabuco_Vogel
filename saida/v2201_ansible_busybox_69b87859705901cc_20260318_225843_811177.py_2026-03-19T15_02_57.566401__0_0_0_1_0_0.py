def remove_user(self):
    cmd = [self.module.get_bin_path('deluser', True), self.name]
    if self.remove:
        cmd.append('--remove-home')
    return self.execute_command(cmd)