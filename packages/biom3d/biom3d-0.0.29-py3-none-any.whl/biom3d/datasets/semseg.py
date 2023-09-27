#---------------------------------------------------------------------------
# Dataset primitives for 3D Nucleus dataset
# trained with data augmentation 
# trained with only a single image
# for speed reasons this images is repeated "batch_size" times
# solution: image resampling approach with npy/tif files
#---------------------------------------------------------------------------

import torch
from torch.utils.data import Dataset
import numpy as np
import pandas as pd
import random 
import os
from skimage.io import imread
from skimage.morphology import erosion, dilation
from biom3d.utils import get_folds_train_test_df
import torchio as tio 

#---------------------------------------------------------------------------
# primitive for 3D semantic segmentation
# can be used only with fixed sized image

class SemSeg3D(Dataset):
    def __init__(self, 
                 img_dir,
                 msk_dir, 
                 folds_csv=None, 
                 fold=0, 
                 val_split=0.5, # exclusive with fold_csv and fold
                 train=True, 
                 use_onehot = False,
                 use_aug = True,
                 ):

        super(Dataset, self).__init__()

        self.img_dir = img_dir
        self.msk_dir = msk_dir
        
        # get the training and validation names 
        if folds_csv is not None:
            df = pd.read_csv(folds_csv)
            trainset, testset = get_folds_train_test_df(df, verbose=False)

            self.fold = fold
            
            self.val_imgs = trainset[self.fold]
            del trainset[self.fold]
            self.train_imgs = []
            for i in trainset: self.train_imgs += i

        else: # tmp: validation split = 50% by default
            all_set = os.listdir(img_dir)
            val_split = int(val_split * len(all_set))
            if val_split == 0: val_split=1
            self.train_imgs = all_set[val_split:]
            self.val_imgs = all_set[:val_split]
            testset = []
            
        self.train = train
        print("current fold: {}\n \
        length of the training set: {}\n \
        length of the validation set: {}\n \
        length of the testing set: {}\n \
        is training mode active?: {}".format(fold, len(self.train_imgs), len(self.val_imgs), len(testset), self.train))

        self.validation_transform = tio.Compose([
            # tio.Resample(spacing),
            # tio.CropOrPad(crop_shape),
        ]+([tio.OneHot()] if use_onehot else []))

        if use_aug:
            self.training_transform = tio.Compose([
                # tio.Resample(spacing),
                # tio.CropOrPad(crop_shape),
                # tio.RandomMotion(p=0.2),
                # tio.RandomBiasField(p=0.3),
                # tio.ZNormalization(masking_method=tio.ZNormalization.mean),
                # tio.RandomNoise(p=0.5),
                tio.RandomFlip(),
                tio.OneOf({
                    tio.RandomAffine(scales=0.1, degrees=10, translation=5): 0.8,
                    tio.RandomElasticDeformation(): 0.2,
                }),
                tio.RandomGamma(),
            ]+([tio.OneHot()] if use_onehot else []))
        else: 
            self.training_transform = self.validation_transform
    
    def __len__(self):
        return len(self.train_imgs) if self.train else len(self.val_imgs)
        
    def __getitem__(self, idx):
        img_fname = self.train_imgs[idx] if self.train else self.val_imgs[idx]
        img_path = os.path.join(self.img_dir, img_fname)
        msk_path = os.path.join(self.msk_dir, img_fname)
        
        # load mask and image
        img = imread(img_path)
        msk = imread(msk_path)
        assert img.shape == msk.shape, '[error] expected img and msk sizes must match, img {}, msk {}'.format(img.shape, msk.shape)
        
        # normalize
        img = (img - img.min()) / (img.max() - img.min())
        # img = img / (2**16 - 1)
        # msk = msk / (2**8 - 1)
        msk = msk / (np.max(msk))
        
        # crop if training
        # if self.train: # TODO: remove resize during inference
        # img, msk = self.resize(img, msk)
        
        # add channel
        img = np.expand_dims(img, 0)
        msk = np.expand_dims(msk, 0)
        
        # to tensor
        img = torch.tensor(img, dtype=torch.float)
        msk = torch.tensor(msk, dtype=torch.float)

        # transform with TorchIO
        transform = self.training_transform if self.train else self.validation_transform
        tmp_sub = transform(tio.Subject(img=tio.ScalarImage(tensor=img), msk=tio.LabelMap(tensor=msk)))
        img, msk = tmp_sub.img.tensor, tmp_sub.msk.tensor

        return img, msk

#---------------------------------------------------------------------------