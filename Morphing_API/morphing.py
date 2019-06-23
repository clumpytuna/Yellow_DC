import numpy as np
import skimage
from skimage import io
from skimage import transform
import os
import matplotlib.pyplot as plt
import random

from get_keypoints import *

dir_path = os.path.dirname(os.path.abspath(__file__))

def load_fruits():
    fruits = []
    mappings = []
    coords = []
    
    with open(os.path.join(dir_path, 'fruits/mapping.csv'), 'r') as m:
        for line in m:
            ar = line.split(',')
            coord = [int(x) for x in ar[1:3]]
            mapping = int(ar[3])
            if ar[0] != '':
                if os.path.exists('fruits/files/Fruit{}_2.png'.format(int(ar[0]))):
                    add = random.choice(['_2', ''])
                else:
                    add = ''
                
                fruit = io.imread(os.path.join(dir_path, 'fruits/files/Fruit{}{}.png'.format(int(ar[0]), add)))
                fruits.append(fruit)
                mappings.append([])
                coords.append([])
            mappings[-1].append(mapping)
            coords[-1].append(coord)
    return fruits, mappings, coords

def get_keypoints_coord(pred):
    flatten = np.argmax(pred.reshape(pred.shape[0], -1), axis=-1)
    result = np.zeros((flatten.shape[0], 2), dtype=int)
    result[:, 1] = flatten // pred.shape[-1]
    result[:, 0] = flatten % pred.shape[-1]
    
    return result

def face_to_fruits(input_path, output_path):
    source = io.imread(os.path.join(dir_path, 'examples/face.jpg'))
    target = io.imread(input_path)
    target = target[:, :, :3]
    target_keypoints_pred = get_keypoints(target).numpy()[0]
    shape = source.shape[:2]
    big_target_keypoints_pred = np.zeros((target_keypoints_pred.shape[0],) + source.shape[:2])

    for i in range(target_keypoints_pred.shape[0]):
        big_target_keypoints_pred[i] = transform.resize(target_keypoints_pred[i], shape)
        
    target_keypoints = get_keypoints_coord(big_target_keypoints_pred)
    
    fruits, mappings, coords = load_fruits()
    
    result = np.zeros_like(source)

    for fruit, mapping, coord in zip(fruits, mappings, coords):
        target_coord = target_keypoints[mapping]
        coord = np.array(coord)
        t = transform.estimate_transform('similarity', coord, target_coord)
        w_fruit = transform.warp(fruit, inverse_map=t.inverse, preserve_range=True)
        mask = (w_fruit[:, :, -1] > 0.5)
        result[mask] = w_fruit[:, :, :3][mask]
    result[result == 0] = 255
    
    plt.imshow(result)
    plt.axis('off')
    plt.savefig(output_path, format='png', dpi=700, bbox_inches='tight', pad_inches=0)
    
    return result