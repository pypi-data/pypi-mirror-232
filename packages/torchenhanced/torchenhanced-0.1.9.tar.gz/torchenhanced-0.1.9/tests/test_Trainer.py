import torch, torch.nn as nn, sys, pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.as_posix())

import torch.optim.lr_scheduler as lrsched
from torch.optim import Optimizer
from torch.utils.data import DataLoader,Subset
# Import mnist for tests
from torchvision.datasets import MNIST
import torch.nn.functional as F
from torchvision import transforms as t
from src.torchenhanced import Trainer, DevModule, ConfigModule
import wandb, os

curfold = pathlib.Path(__file__).parent

class LinSimple(ConfigModule):
    def __init__(self, hidden = 28*28, out =10):
        config = locals()
        del config['self']
        del config['__class__']

        super().__init__(config)

        self.layer = nn.Linear(hidden, out)
    
    def forward(self, x):
        return self.layer(x)
    
class LinearTrainer(Trainer):

    def __init__(self, run_name: str = None, project_name: str = None, state_save_loc=None):

        super().__init__(LinSimple(), run_name=run_name, project_name=project_name,state_save_loc=state_save_loc)

        self.dataset =Subset(MNIST(os.path.join(curfold,'data'),download=True,transform=t.ToTensor()),range(100))
    
    def get_loaders(self, batch_size, num_workers=0):
        return DataLoader(self.dataset, batch_size=batch_size, shuffle=True), None
    
    def process_batch(self, batch_data, data_dict: dict, **kwargs):
        x, y = batch_data
        x = x.reshape((x.shape[0],-1))
        
        pred = self.model(x) # (B,10)
        loss = F.cross_entropy(pred,y,reduction='mean') 

        assert self.stepnum==data_dict['stepnum'], f"Stepnum mismatch {self.stepnum} vs {data_dict['stepnum']}"
        assert self.step_log==data_dict['step_log'], f"Step_log mismatch {self.step_log} vs {data_dict['step_log']}"
        assert self.epoch == data_dict['epoch'], f"Epoch mismatch {self.epoch} vs {data_dict['epoch']}"
        assert self.batchnum == data_dict['batchnum'], f"Batchnum mismatch {self.batchnum} vs {data_dict['batchnum']}"

        if(data_dict['stepnum']%data_dict['step_log']==data_dict['step_log']-1):
            wandb.log({'lossme':loss.item()},commit=False)
        
        return loss, data_dict

# FOR MANUAL TESTING, COULDN'T FIGURE OUT HOW TO AUTOMATE IT
trainer = LinearTrainer(run_name='test_broken_question', project_name='test_torchenhanced', state_save_loc=os.path.join(curfold))
if(os.path.exists(os.path.join(curfold,'test_torchenhanced','state','test_broken_question.state'))):
    trainer.load_state(os.path.join(curfold,'test_torchenhanced','state','test_broken_question.state'))
trainer.train_epochs(epochs=30, batch_size=4, step_log=5, save_every=1, val_log=2)

def test_Save_Weights():
    lintra = LinearTrainer(run_name='test_save_weights', project_name='AnewDawn', state_save_loc=os.path.join(curfold))
    lintra.save_state()

    Trainer.save_model_from_state(state_path=os.path.join(curfold,'AnewDawn','state','test_save_weights.state'),
                                 save_dir=os.path.join(curfold,'AnewDawn'),name='testJEFF')

    assert os.path.isfile(os.path.join(curfold,'AnewDawn','testJEFF.pt')), "Weights not found"
    assert os.path.isfile(os.path.join(curfold,'AnewDawn','testJEFF.config')), "Config not found"

def test_Trainer_config():
    ma = LinSimple(hidden=32,out=15)

    config = ma.config

    assert config == {'hidden':32, 'out':15, 'name':'LinSimple'}, f"Invalid config : {config}"

# Probably need to add more unit_tests...
