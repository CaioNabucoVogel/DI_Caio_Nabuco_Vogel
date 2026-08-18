def __init__(self, ch=128, ch_mult=(1, 2, 4, 4), num_res_blocks=2, in_channels=3, z_channels=16, dtype=torch.float32, device=None):
    super().__init__()
    self.num_resolutions = len(ch_mult)
    self.num_res_blocks = num_res_blocks
    self.conv_in = torch.nn.Conv2d(in_channels, ch, kernel_size=3, stride=1, padding=1, dtype=dtype, device=device)
    in_ch_mult = (1,) + tuple(ch_mult)
    self.in_ch_mult = in_ch_mult
    self.down = torch.nn.ModuleList()
    for i_level in range(self.num_resolutions):
        block = torch.nn.ModuleList()
        attn = torch.nn.ModuleList()
        block_in = ch * in_ch_mult[i_level]
        block_out = ch * ch_mult[i_level]
        for _ in range(num_res_blocks):
            block.append(ResnetBlock(in_channels=block_in, out_channels=block_out, dtype=dtype, device=device))
            block_in = block_out
        down = torch.nn.Module()
        down.block = block
        down.attn = attn
        if i_level != self.num_resolutions - 1:
            down.downsample = Downsample(block_in, dtype=dtype, device=device)
        self.down.append(down)
    self.mid = torch.nn.Module()
    self.mid.block_1 = ResnetBlock(in_channels=block_in, out_channels=block_in, dtype=dtype, device=device)
    self.mid.attn_1 = AttnBlock(block_in, dtype=dtype, device=device)
    self.mid.block_2 = ResnetBlock(in_channels=block_in, out_channels=block_in, dtype=dtype, device=device)
    self.norm_out = Normalize(block_in, dtype=dtype, device=device)
    self.conv_out = torch.nn.Conv2d(block_in, 2 * z_channels, kernel_size=3, stride=1, padding=1, dtype=dtype, device=device)
    self.swish = torch.nn.SiLU(inplace=True)