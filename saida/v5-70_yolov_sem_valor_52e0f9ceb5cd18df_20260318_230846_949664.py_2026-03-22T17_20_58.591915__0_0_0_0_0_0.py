def __init__(self, save_dir=None, weights=None, opt=None, hyp=None, logger=None, include=LOGGERS):
    self.save_dir = save_dir
    self.weights = weights
    self.opt = opt
    self.hyp = hyp
    self.plots = not opt.noplots
    self.logger = logger
    self.include = include
    self.keys = ['train/box_loss', 'train/obj_loss', 'train/cls_loss', 'metrics/precision', 'metrics/recall', 'metrics/mAP_0.5', 'metrics/mAP_0.5:0.95', 'val/box_loss', 'val/obj_loss', 'val/cls_loss', 'x/lr0', 'x/lr1', 'x/lr2']
    self.best_keys = ['best/epoch', 'best/precision', 'best/recall', 'best/mAP_0.5', 'best/mAP_0.5:0.95']
    for k in LOGGERS:
        setattr(self, k, None)
    self.csv = True
    if not clearml:
        prefix = colorstr('ClearML: ')
        s = f"{prefix}run 'pip install clearml' to automatically track, visualize and remotely train YOLOv5 🚀 in ClearML"
        self.logger.info(s)
    if not comet_ml:
        prefix = colorstr('Comet: ')
        s = f"{prefix}run 'pip install comet_ml' to automatically track and visualize YOLOv5 🚀 runs in Comet"
        self.logger.info(s)
    s = self.save_dir
    if 'tb' in self.include and (not self.opt.evolve):
        prefix = colorstr('TensorBoard: ')
        self.logger.info(f"{prefix}Start with 'tensorboard --logdir {s.parent}', view at http://localhost:6006/")
        self.tb = SummaryWriter(str(s))
    if wandb and 'wandb' in self.include:
        wandb_artifact_resume = isinstance(self.opt.resume, str) and self.opt.resume.startswith('wandb-artifact://')
        run_id = torch.load(self.weights).get('wandb_id') if self.opt.resume and (not wandb_artifact_resume) else None
        self.opt.hyp = self.hyp
        self.wandb = WandbLogger(self.opt, run_id)
    else:
        self.wandb = None
    if clearml and 'clearml' in self.include:
        self.clearml = ClearmlLogger(self.opt, self.hyp)
    else:
        self.clearml = None
    if comet_ml and 'comet' in self.include:
        if isinstance(self.opt.resume, str) and self.opt.resume.startswith('comet://'):
            run_id = self.opt.resume.split('/')[-1]
            self.comet_logger = CometLogger(self.opt, self.hyp, run_id=run_id)
        else:
            self.comet_logger = CometLogger(self.opt, self.hyp)
    else:
        self.comet_logger = None