#---------------------------------------------------------------------------
# Original nnUNet dataloader definition
# from: official code of nnUNet
#---------------------------------------------------------------------------

from nnunet.training.network_training.nnUNetTrainerV2 import nnUNetTrainerV2

class nnUNetDataloader(nnUNetTrainerV2):
    def __init__(self,
        plans_file, 
        fold,
        output_folder,
        dataset_directory,
        train=True,
        batch_dice=True,
        stage=1,
        unpack_data=True,
        deterministic=False,
        fp16=True):

        self.train = train

        super().__init__(
            plans_file, 
            fold,
            output_folder,
            dataset_directory,
            batch_dice,
            stage,
            unpack_data,
            deterministic,
            fp16)
        
        self.initialize(True)

        self.__iter__()
    
    def __len__(self):
        if self.train:
            return 250
        else:
            return 50
        
    def __iter__(self):
        self.crt_step = 0
        if self.train:
            self.iter = self.tr_gen
        else:
            self.iter = self.val_gen
        return self
        
    def __next__(self):
        if self.crt_step > self.__len__():
            raise StopIteration
        else: 
            out = next(self.iter)
            self.crt_step += 1
            return out['data'], out['target'][0].long()
