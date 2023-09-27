#---------------------------------------------------------------------------
# A register for all the existing methods
# Aim of this module: 
# - to gather all required imports in a single file
# - to use it in colaboration with a config file
#---------------------------------------------------------------------------

from biom3d.utils import Dict

#---------------------------------------------------------------------------
# dataset register

# import datasets.datasets_old as datasets_old
# from datasets.arcface import ArcFace
from biom3d.datasets.triplet import Triplet
# from biom3d.datasets.triplet_seg import TripletSeg
# from biom3d.datasets.semseg import SemSeg3D
# from datasets.semseg_fast import SemSeg3DFast
# from datasets.semseg_patch import SemSeg3DPatchTrain, SemSeg3DPatchVal
from biom3d.datasets.semseg_patch_fast import SemSeg3DPatchFast
from biom3d.datasets.semseg_torchio import TorchioDataset
# from datasets.model_genesis import Genesis
# from datasets.denoiseg import DenoiSeg
# from datasets.adversarial import Adversarial
from biom3d.datasets.dino import Dino
from biom3d.datasets.arcface import ArcFace
from biom3d.datasets.swin_trans import SSLSwin
from biom3d.datasets.nnunet import nnUNetDataloader
from biom3d.datasets.semseg_torchio import TorchioDataset
from biom3d.datasets.semseg_batchgen import MTBatchGenDataLoader

datasets = Dict(
    # Seg             =Dict(fct=SemSeg3D, kwargs=Dict()),
    # SegFast         =Dict(fct=SemSeg3DFast, kwargs=Dict()),
    # SingleNucleus   =Dict(fct=datasets_old.Nucleus3DSingle, kwargs=Dict()),
    Triplet         =Dict(fct=Triplet, kwargs=Dict()),
    # TripletSeg      =Dict(fct=TripletSeg, kwargs=Dict()),
    # ArcFace         =Dict(fct=ArcFace, kwargs=Dict()),
    # CoTrain         =Dict(fct=datasets_old.CoTrain, kwargs=Dict()),
    # SegPatchTrain   =Dict(fct=SemSeg3DPatchTrain, kwargs=Dict()),
    # SegPatchVal     =Dict(fct=SemSeg3DPatchVal, kwargs=Dict()),
    SegPatchFast    =Dict(fct=SemSeg3DPatchFast, kwargs=Dict()),
    Torchio         =Dict(fct=TorchioDataset, kwargs=Dict()),
    nnUNet          =Dict(fct=nnUNetDataloader, kwargs=Dict()),
    # Genesis         =Dict(fct=Genesis, kwargs=Dict()),
    # DenoiSeg        =Dict(fct=DenoiSeg, kwargs=Dict()),
    # Adversarial     =Dict(fct=Adversarial, kwargs=Dict()),
    Dino            =Dict(fct=Dino, kwargs=Dict()),
    ArcFace         =Dict(fct=ArcFace, kwargs=Dict()),
    SSLSwin         =Dict(fct=SSLSwin, kwargs=Dict()),
    BatchGen        =Dict(fct=MTBatchGenDataLoader, kwargs=Dict()),
)

try:
    from biom3d.datasets.semseg_batchgen import MTBatchGenDataLoader
    datasets.BatchGen = Dict(fct=MTBatchGenDataLoader, kwargs=Dict())
except:
    pass

#---------------------------------------------------------------------------
# model register

from biom3d.models.unet3d_vgg_deep import CotUNet, NNet, unet3d_vgg_triplet, UNet
from biom3d.models.encoder_vgg import VGGEncoder, EncoderBlock
from biom3d.models.encoder_efficientnet3d import EfficientNet3D
from biom3d.models.unet3d_eff_2 import FPN
from biom3d.models.unet3d_eff_3 import EffUNet
from biom3d.models.head import dino, hrnet_mlp, vgg_mlp
# from archive.models.unet3d_monai import BasicUNet
# from monai.networks import nets
from biom3d.models.hrnet_2 import HighResolutionNet
from biom3d.models.swinvit import SwinUNETR
from biom3d.models.ssl_swinvit import SSLHead
from biom3d.models.ssl_vgg import SSLVGG

models = Dict(
    UNet3DVGGDeep   =Dict(fct=UNet, kwargs=Dict()),
    # BasicUNetMonai  =Dict(fct=nets.BasicUNet, kwargs=Dict(spatial_dims=3, features=(32, 32, 64, 128, 256, 32))),
    # UNetMonai       =Dict(fct=nets.AttentionUnet, kwargs=Dict()),
    VGG3D           =Dict(fct=VGGEncoder, kwargs=Dict(block=EncoderBlock, use_head=True)),
    Eff3D           =Dict(fct=EfficientNet3D.from_name, kwargs=Dict()),
    EffUNet         =Dict(fct=EffUNet, kwargs=Dict()),
    FPN             =Dict(fct=FPN, kwargs=Dict(
                        encoder=EfficientNet3D.from_name("efficientnet-b4", override_params={'num_classes': 256}, in_channels=1, num_pools=[3,5,5]),)),
    TripletUNet     =Dict(fct=unet3d_vgg_triplet, kwargs=Dict()),
    SelfDino        =Dict(fct=dino, kwargs=Dict()),
    VGG3DMLP        =Dict(fct=vgg_mlp, kwargs=Dict()),
    NNet            =Dict(fct=NNet, kwargs=Dict()),
    CotUNet         =Dict(fct=CotUNet, kwargs=Dict()),
    HRNet           =Dict(fct=HighResolutionNet, kwargs=Dict()),
    HRNetMLP        =Dict(fct=hrnet_mlp, kwargs=Dict()),
    Swin            =Dict(fct=SwinUNETR, kwargs=Dict()),
    SSLSwin         =Dict(fct=SSLHead, kwargs=Dict()),
    SSLVGG          =Dict(fct=SSLVGG, kwargs=Dict()),
)

#---------------------------------------------------------------------------
# metric register

import biom3d.metrics as mt

metrics = Dict(
    Dice        =Dict(fct=mt.Dice, kwargs=Dict()),
    DiceBCE     =Dict(fct=mt.DiceBCE, kwargs=Dict()),
    DiceCEnnUNet=Dict(fct=mt.DC_and_CE_loss, kwargs=Dict(soft_dice_kwargs={'batch_dice': True, 'smooth': 1e-5, 'do_bg': False}, ce_kwargs={})),
    IoU         =Dict(fct=mt.IoU, kwargs=Dict()),
    # IoUChannel  =Dict(fct=mt.IoUChannel, kwargs=Dict()),
    MSE         =Dict(fct=mt.MSE, kwargs=Dict()),
    CE          =Dict(fct=mt.CrossEntropy, kwargs=Dict()),
    DeepMSE     =Dict(fct=mt.DeepMetric, kwargs=Dict(metric=mt.MSE)),
    DeepDiceBCE =Dict(fct=mt.DeepMetric, kwargs=Dict(metric=mt.DiceBCE)),
    Triplet     =Dict(fct=mt.Triplet, kwargs=Dict()),
    TripletSeg  =Dict(fct=mt.TripletDiceBCE, kwargs=Dict()),
    # NNTriplet   =Dict(fct=mt.NNTriplet, kwargs=Dict()),
    ArcFace     =Dict(fct=mt.ArcFace, kwargs=Dict()),
    FocalLoss   =Dict(fct=mt.FocalLoss, kwargs=Dict()),
    CoTrain     =Dict(fct=mt.CoTrain, kwargs=Dict()),
    DenoiSeg    =Dict(fct=mt.DenoiSeg, kwargs=Dict()),
    Adversarial =Dict(fct=mt.Adversarial, kwargs=Dict()),
    DiceAdverse =Dict(fct=mt.DiceAdversarial, kwargs=Dict()),
    Dino        =Dict(fct=mt.DINOLoss, kwargs=Dict()),
    KLDiv       =Dict(fct=mt.KLDiv, kwargs=Dict()),
    Entropy     =Dict(fct=mt.Entropy, kwargs=Dict()),
    HRDiceBCE   =Dict(fct=mt.HRDiceBCE, kwargs=Dict()),
    SSLSwinLoss =Dict(fct=mt.SSLRotContrastRecons, kwargs=Dict()),
)

#---------------------------------------------------------------------------
# trainer register

from biom3d.trainers import (
    denoiseg_train,
    denoiseg_val,
    dino_train,
    seg_train, 
    seg_validate,
    triplet_seg_train, 
    triplet_train,
    triplet_val,
    arcface_train,
    arcface_val,
    adverse_train,
    cotrain_train,
    cotrain_validate,
    seg_patch_validate,
    seg_patch_train,
    ssl_swinvit,
)

trainers = Dict(
    SegTrain        =Dict(fct=seg_train, kwargs=Dict()),
    SegVal          =Dict(fct=seg_validate, kwargs=Dict()),
    SegPatchTrain   =Dict(fct=seg_patch_train, kwargs=Dict()),
    SegPatchVal     =Dict(fct=seg_patch_validate, kwargs=Dict()),
    TripletTrain    =Dict(fct=triplet_train, kwargs=Dict()),
    TripletVal      =Dict(fct=triplet_val, kwargs=Dict()),
    TripletSegTrain =Dict(fct=triplet_seg_train, kwargs=Dict()),
    ArcFaceTrain    =Dict(fct=arcface_train, kwargs=Dict()),
    ArcFaceVal      =Dict(fct=arcface_val, kwargs=Dict()),
    AdverseTrain    =Dict(fct=adverse_train, kwargs=Dict()),
    CoTrainTrain    =Dict(fct=cotrain_train,  kwargs=Dict()),
    CoTrainVal      =Dict(fct=cotrain_validate,  kwargs=Dict()),
    DenoiSegTrain   =Dict(fct=denoiseg_train, kwargs=Dict()),
    DenoiSegVal     =Dict(fct=denoiseg_val, kwargs=Dict()),
    DinoTrain       =Dict(fct=dino_train, kwargs=Dict()),
    SSLSwinTrain    =Dict(fct=ssl_swinvit, kwargs=Dict()),
)

#---------------------------------------------------------------------------
# Preprocessor and predictor register
# We register preprocessors here because they are needed to preprocess
# data before prediction.
# Preprocessor must correspond to the one used to preprocess data
# before training.

from biom3d.preprocess import seg_preprocessor

preprocessors = Dict(
    Seg = Dict(fct=seg_preprocessor, kwargs=Dict())
)

from biom3d.predictors import (
    seg_predict,
    seg_predict_patch_2,
)

predictors = Dict(
    Seg = Dict(fct=seg_predict, kwargs=Dict()),
    SegPatch = Dict(fct=seg_predict_patch_2, kwargs=Dict()),
)

from biom3d.predictors import seg_postprocessing

postprocessors = Dict(
    Seg = Dict(fct=seg_postprocessing, kwargs=Dict())
)

#---------------------------------------------------------------------------
# Display utils

# import argparse

# if __name__=="__main__":
#     parser = argparse.ArgumentParser(description="Register of all modules in biom3d.")
#     parser.add_argument("--one", type=str, default=None,
#         help="Print one specific documentation of one module given its category:name in the register.")  
#     parser.add_argument("--all", default=False,  action='store_true', dest='all',
#         help="Print the documentation of all the modules.")
#     args = parser.parse_args()

#     all_cat = [datasets, models, metrics, trainers, preprocessors, predictors, postprocessors]

#     if args.all:
#         for cat in all_cat:
#             for k,v in cat.items():
#                 print("Module:", k)
#                 if v['fct'].__doc__ is not None:
#                     print(v['fct'].__doc__)
#                 print("")
#     elif args.one is not None:
#         # check if it is a valid category
        

#         # check if it is a valid name
#         idx_valid=-1
#         for i,cat in enumerate(all_cat):
#             if args.one in cat.keys():
#                 idx_valid = i
#         if idx_valid<0:
#             print("[Error] Not a correct name:", args.one)
#             raise RuntimeError
#         else:
#             help(all_cat[idx_valid][args.one]['fct'])


#---------------------------------------------------------------------------
