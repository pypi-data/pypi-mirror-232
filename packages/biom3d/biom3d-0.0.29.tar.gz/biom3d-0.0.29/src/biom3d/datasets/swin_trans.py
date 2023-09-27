#---------------------------------------------------------------------------
# Dataset primitives for 3D segmentation dataset
# solution: patch approach with the whole dataset into memory 
#---------------------------------------------------------------------------

from json import load
import os
import numpy as np 
from numpy.random import randint
import torchio as tio
import random 
import torch
from torch.utils.data import Dataset, DataLoader
# from monai.data import CacheDataset
import pandas as pd 
from tqdm import tqdm 
from skimage.io import imread

from biom3d.utils import centered_pad, get_folds_train_test_df

#---------------------------------------------------------------------------
# from https://github.com/Project-MONAI/research-contributions/blob/main/SwinUNETR/Pretrain/utils/ops.py 

def patch_rand_drop(x, x_rep=None, max_drop=0.3, max_block_sz=0.25, tolr=0.05):
    c, h, w, z = x.size()
    n_drop_pix = np.random.uniform(0, max_drop) * h * w * z
    mx_blk_height = int(h * max_block_sz)
    mx_blk_width = int(w * max_block_sz)
    mx_blk_slices = int(z * max_block_sz)
    tolr = (int(tolr * h), int(tolr * w), int(tolr * z))
    total_pix = 0
    while total_pix < n_drop_pix:
        rnd_r = randint(0, h - tolr[0])
        rnd_c = randint(0, w - tolr[1])
        rnd_s = randint(0, z - tolr[2])
        rnd_h = min(randint(tolr[0], mx_blk_height) + rnd_r, h)
        rnd_w = min(randint(tolr[1], mx_blk_width) + rnd_c, w)
        rnd_z = min(randint(tolr[2], mx_blk_slices) + rnd_s, z)
        if x_rep is None:
            x_uninitialized = torch.empty(
#                 (c, rnd_h - rnd_r, rnd_w - rnd_c, rnd_z - rnd_s), dtype=x.dtype, device=args.local_rank
                (c, rnd_h - rnd_r, rnd_w - rnd_c, rnd_z - rnd_s), dtype=x.dtype,
            ).normal_()
            x_uninitialized = (x_uninitialized - torch.min(x_uninitialized)) / (
                torch.max(x_uninitialized) - torch.min(x_uninitialized)
            )
            x[:, rnd_r:rnd_h, rnd_c:rnd_w, rnd_s:rnd_z] = x_uninitialized
        else:
            x[:, rnd_r:rnd_h, rnd_c:rnd_w, rnd_s:rnd_z] = x_rep[:, rnd_r:rnd_h, rnd_c:rnd_w, rnd_s:rnd_z]
        total_pix = total_pix + (rnd_h - rnd_r) * (rnd_w - rnd_c) * (rnd_z - rnd_s)
    return x

def aug_rand(args, samples):
    img_n = samples.size()[0]
    x_aug = samples.detach().clone()
    for i in range(img_n):
        x_aug[i] = patch_rand_drop(x_aug[i])
        idx_rnd = randint(0, img_n)
        if idx_rnd != i:
            x_aug[i] = patch_rand_drop(x_aug[i], x_aug[idx_rnd])
    return x_aug

#---------------------------------------------------------------------------
# translation into functions made for numpy arrays of the orginal SSL SwinVIT
# pretraining

def rot_rand(x):
    """
    Random rotation of 90 degrees applied on the (2,3) axes.
    
    orignal version:
    ----------------
    def rot_rand(args, x_s):
        img_n = x_s.size()[0]
        x_aug = x_s.detach().clone()
        device = torch.device(f"cuda:{args.local_rank}")
        x_rot = torch.zeros(img_n).long().to(device)
        for i in range(img_n):
            x = x_s[i]
            orientation = np.random.randint(0, 4)
            if orientation == 0:
                pass
            elif orientation == 1:
                x = x.rot90(1, (2, 3))
            elif orientation == 2:
                x = x.rot90(2, (2, 3))
            elif orientation == 3:
                x = x.rot90(3, (2, 3))
            x_aug[i] = x
            x_rot[i] = orientation
        return x_aug, x_rot
    """
    
    orientation = np.random.randint(0, 4)
    if orientation == 0:
        pass
    elif orientation == 1:
        x = torch.rot90(x, 1, (2, 3))
    elif orientation == 2:
        x = torch.rot90(x, 2, (2, 3))
    elif orientation == 3:
        x = torch.rot90(x, 3, (2, 3))
    return x, orientation
    

#---------------------------------------------------------------------------
# utilities to random crops

def random_crop(img, crop_shape):
    """
    randomly crop a portion of size prop of the original image size.
    """
    img_shape = np.array(img.shape)[1:]
    # rand_start = np.array([random.randint(0,c) for c in np.maximum(0,(img_shape-crop_shape))])
    rand_start = np.random.randint(0, np.maximum(1,img_shape-crop_shape))
    rand_end = crop_shape+rand_start

    crop_img = img[:,
                    rand_start[0]:rand_end[0], 
                    rand_start[1]:rand_end[1], 
                    rand_start[2]:rand_end[2]]
    return crop_img

def random_pad(img, final_size):
    """
    randomly pad an image with zeros to reach the final size. 
    if the image is bigger than the expected size, then the image is cropped.
    """
    img_shape = np.array(img.shape)[1:]
    size_range = (final_size-img_shape) * (final_size-img_shape > 0) # needed if the original image is bigger than the final one
    # rand_start = np.array([random.randint(0,c) for c in size_range])
    rand_start = np.random.randint(0,np.maximum(1,size_range))

    rand_end = final_size-(img_shape+rand_start)
    rand_end = rand_end * (rand_end > 0)

    pad = np.append([[0,0]],np.vstack((rand_start, rand_end)).T,axis=0)
    pad_img = np.pad(img, pad, 'constant', constant_values=0)
    # pad_img = torch.nn.functional.pad(img, tuple(pad.flatten().tolist()), 'constant', value=0)

    # crop the image if needed
    if ((final_size-img_shape) < 0).any(): # keeps only the negative values
        pad_img = pad_img[:,:final_size[0],:final_size[1],:final_size[2]]
    return pad_img

def random_crop_pad(img, final_size):
    """
    random crop and pad if needed.
    """
    # or random crop
    img = random_crop(img, final_size)

    # pad if needed
    if (np.array(img.shape)[1:]-final_size).sum()!=0:
        img = centered_pad(img, final_size)
    return img

#---------------------------------------------------------------------------

class SSLSwin(Dataset):
    """
    with DataLoader
    """
    def __init__(
        self,
        img_dir,
        batch_size, 
        patch_size,
        nbof_steps,
        folds_csv  = None, 
        fold       = 0, 
        val_split  = 0.25,
        train      = True,
        ):

        self.img_dir = img_dir

        self.batch_size = batch_size
        self.patch_size = patch_size

        self.nbof_steps = nbof_steps
        
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
            val_split = np.round(val_split * len(all_set)).astype(int)
            self.train_imgs = all_set[val_split:]
            self.val_imgs = all_set[:val_split]
            testset = []
        
            
        self.train = train
        print("current fold: {}\n \
        length of the training set: {}\n \
        length of the validation set: {}\n \
        length of the testing set: {}\n \
        is training mode active?: {}".format(fold, len(self.train_imgs), len(self.val_imgs), len(testset), self.train))

        # print train and validation image names
        print("Training images:", self.train_imgs)
        print("Validation images:", self.val_imgs)

        ps = np.array(self.patch_size)
    
    def __len__(self):
        return self.nbof_steps*self.batch_size
    
    def __getitem__(self, idx):

        fnames = self.train_imgs if self.train else self.val_imgs
        img_fname = fnames[idx%len(fnames)]

        # file name
        img_path = os.path.join(self.img_dir, img_fname)

        # read the image
        img = imread(img_path)

        # crop the image
        x = random_crop_pad(img, final_size=self.patch_size,)
    
        # transform to tensor to fit the expectations of the following augmentations
        x = torch.from_numpy(x)

        # data augmentation
        x1, rot1 = rot_rand(x)
        x2, rot2 = rot_rand(x)
        x1_augment = patch_rand_drop(x1)
        x2_augment = patch_rand_drop(x2)
        x1_augment = x1_augment
        x2_augment = x2_augment

        return x1_augment, x2_augment, rot1, rot2, x1, x2

#---------------------------------------------------------------------------