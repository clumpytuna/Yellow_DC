import torch
import torch.nn as nn

import skimage.transform as transform
import numpy as np
import os

from models.hrnet import get_face_alignment_net
from config import config, update_config

dir_path = os.path.dirname(os.path.abspath(__file__))

def get_raw_keypoints(image, keypoints_dataset='WFLW', device='cpu'):
    assert keypoints_dataset in ['WFLW']
    DSET2CFG = {'COFW': [os.path.join(dir_path, 'experiments/cofw/face_alignment_cofw_hrnet_w18.yaml'),
                     os.path.join(dir_path, 'model_weights/HR18-COFW.pth'), 68],
                'AFLW': ['experiments/aflw/face_alignment_aflw_hrnet_w18.yaml', 
                     'model_weights/HR18-AFLW.pth', 21],
                'WFLW': [os.path.join(dir_path, 'experiments/wflw/face_alignment_wflw_hrnet_w18.yaml'),
                     os.path.join(dir_path, 'model_weights/HR18-WFLW.pth'), 68]
    }
    """Make strange steps"""
    class MyParams:
        cfg = DSET2CFG[keypoints_dataset][0]
        model_file = DSET2CFG[keypoints_dataset][1]
    params = MyParams()

    update_config(config, params)
    config.defrost()
    config.MODEL.INIT_WEIGHTS = False
    config.freeze()
    
    """Load model and resize image"""
    model = get_face_alignment_net(config).to(device)
    if device == 'cpu':
        state_dict = torch.load(params.model_file, map_location='cpu')
    else:
        state_dict = torch.load(params.model_file)
    model.load_state_dict(state_dict)

    resized_img = transform.resize(image, (256, 256), anti_aliasing=True)

    """Convert to tensor and pass through model"""
    vec = np.array(resized_img, dtype=np.float32)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    vec = (vec/vec.max() - mean) / std
    inputs = torch.FloatTensor(vec.transpose([2, 0, 1])).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        output = model(inputs)
    return output.cpu()

def get_keypoints(image, keypoints_dataset='WFLW', device='cpu'):
    raw_keypoints = get_raw_keypoints(image, keypoints_dataset, device)

    """Upscale checkpoints to have shape of (256, 256)"""
    m = nn.Upsample(scale_factor=4, mode='bilinear') 
    with torch.no_grad():
        keypoints = m(raw_keypoints)
    return keypoints

def apply_mask(image, mask, color, alpha=1.0):
    """Apply the given mask to the image.
    """
    for c in range(3):
        image[:, :, c] = np.where(
               mask == 1,
               image[:, :, c] *
               (1 - alpha) + alpha * color[c] * 255,
               image[:, :, c])
    return image

def transform_img_with_keypoints(image, keypoints_dataset='WFLW', device='cpu'):
    keypoints = get_keypoints(image, keypoints_dataset, device)

    modified_img = transform.resize(image, (256, 256), anti_aliasing=True)
    rc = np.array([1, 0, 0])
    for i in range(keypoints.size(1)):
        mask = (keypoints[0, i] >= keypoints[0, i].max())
        modified_img = apply_mask(modified_img, mask, color=rc)

    final_img = transform.resize(modified_img, image.shape, anti_aliasing=True)
    return final_img
