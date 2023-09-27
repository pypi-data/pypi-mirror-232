#---------------------------------------------------------------------------
# Triplet segmentation project
#---------------------------------------------------------------------------

from json import load
import os
from datasets.semseg_patch_fast import SemSeg3DPatchFast
from datasets.triplet import Triplet
import numpy as np 
import torchio as tio
import random 
import torch
from torch.utils.data import Dataset, DataLoader
# from monai.data import CacheDataset
import pandas as pd 
from tqdm import tqdm 
from skimage.io import imread

#---------------------------------------------------------------------------
# utilities to random crops

class DatasetHolder:
    """
    This class was created to access triplet and seg datasets parameters such as:
        -the foreground rate of the seg dataset
        -the overlapping rate of the triplet dataset
    """
    def __init__(
        self,
        batch_size,
        seg_dataset,
        triplet_dataset,
        num_workers,
        ):
        self.batch_size = batch_size 
        self.num_workers = num_workers
        self.seg_dataset = seg_dataset
        self.triplet_dataset = triplet_dataset

        self.seg_dataloader = DataLoader(
            self.seg_dataset,
            batch_size  =batch_size, 
            drop_last   =True, 
            shuffle     =True, 
            num_workers =num_workers, 
            pin_memory  =True,
        )

        self.triplet_dataloader = DataLoader(
            self.triplet_dataset,
            batch_size  =batch_size, 
            drop_last   =False, 
            shuffle     =True, 
            num_workers =num_workers, 
            pin_memory  =True,
        )
    
    def set_min_overlap(self, value):
        self.triplet_dataset.set_min_overlap(value)

        del self.triplet_dataloader
        self.triplet_dataloader = DataLoader(
            self.triplet_dataset,
            batch_size  =self.batch_size, 
            drop_last   =False, 
            shuffle     =True, 
            num_workers =self.num_workers, 
            pin_memory  =True,
        )

    
    def set_fg_rate(self, value):
        self.seg_dataset.set_fg_rate(value)

        del self.seg_dataloader
        self.seg_dataloader = DataLoader(
            self.seg_dataset,
            batch_size  =self.batch_size, 
            drop_last   =True, 
            shuffle     =True, 
            num_workers =self.num_workers, 
            pin_memory  =True,
        )


class TripletSeg:
    def __init__(
        self,
        img_dir,
        msk_dir,
        batch_size, 
        patch_size,
        nbof_steps,
        folds_csv  = None, 
        fold       = 0, 
        val_split  = 0.25,
        train      = True,
        use_aug    = True,
        aug_patch_size = None,
        fg_rate = 0.33, # if > 0, force the use of foreground, needs to run some pre-computations (note: better use the foreground scheduler)
        crop_scale = 1.0, # if > 1, then use random_crop_resize instead of random_crop_pad
        use_softmax = True, # if true, means that the output is one_hot encoded for softmax use
        num_workers = 4,
        ):

        self.seg_dataset = SemSeg3DPatchFast(
            img_dir,
            msk_dir,
            batch_size, 
            patch_size,
            nbof_steps,
            folds_csv  = folds_csv, 
            fold       = fold, 
            val_split  = val_split,
            train      = train,
            use_aug    = use_aug,
            aug_patch_size = aug_patch_size,
            fg_rate = fg_rate, # if > 0, force the use of foreground, needs to run some pre-computations (note: better use the foreground scheduler)
            crop_scale = crop_scale, # if > 1, then use random_crop_resize instead of random_crop_pad
            use_softmax = use_softmax,
        )

        self.triplet_dataset = Triplet(
            img_dir=img_dir,
            batch_size=batch_size, 
            patch_size=patch_size,
            nbof_steps=nbof_steps,
            val_split  = 0,
            train      = train,
            use_aug    = use_aug,
            aug_patch_size = aug_patch_size,
        )

        self.dataset = DatasetHolder(batch_size, self.seg_dataset, self.triplet_dataset, num_workers)

        self.seg_dataloader = self.dataset.seg_dataloader
        self.triplet_dataloader = self.dataset.triplet_dataloader
    
    def __len__(self):
        return len(self.seg_dataloader)