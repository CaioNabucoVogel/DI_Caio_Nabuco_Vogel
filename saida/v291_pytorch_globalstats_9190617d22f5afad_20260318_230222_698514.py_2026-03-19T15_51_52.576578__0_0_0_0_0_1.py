def report(self):
    subs = (('autotune_local', self.autotune_local), ('autotune_remote', self.autotune_remote), ('bundled_autotune', self.bundled_autotune), ('fx_graph', self.fx_graph), ('triton', self.triton), ('aot_autograd', self.aot_autograd), ('dynamo_pgo', self.dynamo_pgo))
    print('Cache Stats:', file=sys.stderr)
    for (name, sub) in subs:
        print(f'  {name}: {sub}', file=sys.stderr)
    print('Cache Entries:', file=sys.stderr)
    for (name, sub) in subs:
        if sub.cache:
            print(f'  {name}:', file=sys.stderr)
            for (k, v) in sorted(sub.cache.items()):
                v = repr(v)
                if len(v) > 100:
                    v = v[:100] + '...'
                print(f'    {k!r}: {v}', file=sys.stderr)