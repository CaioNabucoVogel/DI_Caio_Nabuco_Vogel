def create_user(self):
    cmd = [self.module.get_bin_path('adduser', True)]
    cmd.append('-D')
    if self.uid is not None:
        cmd.append('-u')
        cmd.append(self.uid)
    if self.group is not None:
        if not self.group_exists(self.group):
            self.module.fail_json(msg='Group {0} does not exist'.format(self.group))
        cmd.append('-G')
        cmd.append(self.group)
    if self.comment is not None:
        cmd.append('-g')
        cmd.append(self.comment)
    if self.home is not None:
        cmd.append('-h')
        cmd.append(self.home)
    if self.shell is not None:
        cmd.append('-s')
        cmd.append(self.shell)
    if not self.create_home:
        cmd.append('-H')
    if self.skeleton is not None:
        cmd.append('-k')
        cmd.append(self.skeleton)
    if self.umask is not None:
        cmd.append('-K')
        cmd.append('UMASK=' + self.umask)
    if self.system:
        cmd.append('-S')
    if self.uid_min is not None:
        cmd.append('-K')
        cmd.append('UID_MIN=' + str(self.uid_min))
    if self.uid_max is not None:
        cmd.append('-K')
        cmd.append('UID_MAX=' + str(self.uid_max))
    cmd.append(self.name)
    (rc, out, err) = self.execute_command(cmd)
    if rc is not None and rc != 0:
        self.module.fail_json(name=self.name, msg=err, rc=rc)
    if self.password is not None:
        cmd = [self.module.get_bin_path('chpasswd', True)]
        cmd.append('--encrypted')
        data = '{name}:{password}'.format(name=self.name, password=self.password)
        (rc, out, err) = self.execute_command(cmd, data=data)
        if rc is not None and rc != 0:
            self.module.fail_json(name=self.name, msg=err, rc=rc)
    if self.groups is not None and len(self.groups):
        groups = self.get_groups_set()
        add_cmd_bin = self.module.get_bin_path('adduser', True)
        for group in groups:
            cmd = [add_cmd_bin, self.name, group]
            (rc, out, err) = self.execute_command(cmd)
            if rc is not None and rc != 0:
                self.module.fail_json(name=self.name, msg=err, rc=rc)
    return (rc, out, err)