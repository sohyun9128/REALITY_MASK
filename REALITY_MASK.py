# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j6rlA8c0bODb-UTy7RcgSViMyCLfscIf
"""

# Commented out IPython magic to ensure Python compatibility.

from IPython import display
from PIL import Image

# %tensorflow_version 1.x
import tensorflow as tf
import sys
sys.path.insert(0, 'tpu/models/official')
sys.path.insert(0, 'tpu/models/official/mask_rcnn')
import coco_metric
from mask_rcnn.object_detection import visualization_utils

import cv2
import os

import numpy as np
import pandas as pd
import glob
import natsort 
import time
import math

import logging

#######################################################################################


# 캡쳐 이미지파일 저장할 경로
imgs_path = '/content/imgs'  


# 테스트 비디오 경로
test_video_path = '/content/final_test.mp4'  


# output file 저장 경로
output_path = '/content/output'


# 최종 파일 경로 + 이름
final_path = '/content/reality_data.txt'


# gpu 사용
use_gpu= True #@param {type:"boolean"}

if use_gpu:
  session = tf.Session(config=tf.ConfigProto(log_device_placement=True))
else:
  session = tf.Session(graph=tf.Graph())

saved_model_dir = 'gs://cloud-tpu-checkpoints/mask-rcnn/1555659850' #@param {type:"string"}
_ = tf.saved_model.loader.load(session, ['serve'], saved_model_dir)


ID_MAPPING = {
    1: 'person',
    2: 'bicycle',
    3: 'car',
    4: 'motorcycle',
    5: 'airplane',
    6: 'bus',
    7: 'train',
    8: 'truck',
    9: 'boat',
    10: 'traffic light',
    11: 'fire hydrant',
    13: 'stop sign',
    14: 'parking meter',
    15: 'bench',
    16: 'bird',
    17: 'cat',
    18: 'dog',
    19: 'horse',
    20: 'sheep',
    21: 'cow',
    22: 'elephant',
    23: 'bear',
    24: 'zebra',
    25: 'giraffe',
    27: 'backpack',
    28: 'umbrella',
    31: 'handbag',
    32: 'tie',
    33: 'suitcase',
    34: 'frisbee',
    35: 'skis',
    36: 'snowboard',
    37: 'sports ball',
    38: 'kite',
    39: 'baseball bat',
    40: 'baseball glove',
    41: 'skateboard',
    42: 'surfboard',
    43: 'tennis racket',
    44: 'bottle',
    46: 'wine glass',
    47: 'cup',
    48: 'fork',
    49: 'knife',
    50: 'spoon',
    51: 'bowl',
    52: 'banana',
    53: 'apple',
    54: 'sandwich',
    55: 'orange',
    56: 'broccoli',
    57: 'carrot',
    58: 'hot dog',
    59: 'pizza',
    60: 'donut',
    61: 'cake',
    62: 'chair',
    63: 'couch',
    64: 'potted plant',
    65: 'bed',
    67: 'dining table',
    70: 'toilet',
    72: 'tv',
    73: 'laptop',
    74: 'mouse',
    75: 'remote',
    76: 'keyboard',
    77: 'cell phone',
    78: 'microwave',
    79: 'oven',
    80: 'toaster',
    81: 'sink',
    82: 'refrigerator',
    84: 'book',
    85: 'clock',
    86: 'vase',
    87: 'scissors',
    88: 'teddy bear',
    89: 'hair drier',
    90: 'toothbrush',
}
category_index = {k: {'id': k, 'name': ID_MAPPING[k]} for k in ID_MAPPING}


#######################################################################################


"""
toImages(): 
    동영상을 이미지로 변환해주는 함수.

Args:
    - img_path: 변환할 이미지를 저장할 경로.
    - input_video_file: 이미지로 변환할 비디오 경로.

Returns:
    
"""
def toImages(img_path, input_video_file):

    cam = cv2.VideoCapture(input_video_file)
    counter = 0
    while True:
        flag, frame = cam.read()
        if flag:
            cv2.imwrite(os.path.join(img_path, str(counter) + '.jpg'),frame)
            counter = counter + 1
        else:
            break
        if cv2.waitKey(1) == 27:
            break
    cv2.destroyAllWindows()




"""
maskRcnn
"""
def maskRcnn(imgs_path):
    imgs= glob.glob(imgs_path+'/*.jpg')
    imgs =  natsort.natsorted(imgs)

    csv_idx = 0
    final_df = pd.DataFrame(columns=['id', 'x', 'y'])

    logging.warning('detection start')
    for image_path in imgs:
      with open(image_path, 'rb') as f:
        np_image_string = np.array([f.read()])
      
      image = Image.open(image_path)
      width, height = image.size
      np_image = np.array(image.getdata()).reshape(height, width, 3).astype(np.uint8)


      num_detections, detection_boxes, detection_classes, detection_scores, detection_masks, image_info = session.run(
          ['NumDetections:0', 'DetectionBoxes:0', 'DetectionClasses:0', 'DetectionScores:0', 'DetectionMasks:0', 'ImageInfo:0'],
          feed_dict={'Placeholder:0': np_image_string})

      num_detections = np.squeeze(num_detections.astype(np.int32), axis=(0,))
      detection_boxes = np.squeeze(detection_boxes * image_info[0, 2], axis=(0,))[0:num_detections]
      detection_scores = np.squeeze(detection_scores, axis=(0,))[0:num_detections]
      detection_classes = np.squeeze(detection_classes.astype(np.int32), axis=(0,))[0:num_detections]
      instance_masks = np.squeeze(detection_masks, axis=(0,))[0:num_detections]

    
      point = []

      for idx in range(len(detection_boxes)):
        if detection_classes[idx]==1 and detection_scores[idx]>=0.15:
              ymin, xmin, ymax, xmax = detection_boxes[idx]
              
              point.append([(xmin+xmax)/2, (-1)*(ymin+ymax)/2])

      x = [X[0] for X in point]
      y = [Y[1] for Y in point]

      xy = pd.DataFrame({'id' : "Person", 'x' : x, 'y': y})
      name = output_path + '/' +  str(csv_idx) + '.txt'
      xy.to_csv(name, sep='\t', header=False, index=False)
      csv_idx += 1
      logging.warning('Finish', name)



def distance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)



"""
objectIndexing(): 
    같은 Class에 속하는 객체들을 구분하여 id값을 지정해주는 함수

Args:
    - beforeF, afterF : 연이은 프레임의 객체 인식 정보
    - max_id : id의 최대값

Returns:
    - [해당 프레임 객체들의 id 값이 담긴 list, 업데이트 된 max_id]
    
"""
def objectIndexing(beforeF, afterF, max_id):
    
    # 객체의 수 변화X
    if len(beforeF.index) == len(afterF.index):
      afteridx = list(range(len(afterF.index)))
      for beforeIdx in range(len(beforeF.index)):
          x = beforeF['x'][beforeIdx]
          y = beforeF['y'][beforeIdx]
          minidx = -1
          mindis = 999
          for afterCount in afteridx:
            dis = distance(x, y, afterF['x'][afterCount], afterF['y'][afterCount])
            if mindis > dis:
              minidx = afterCount
              mindis = dis
          afterF['id'][minidx] = beforeF['id'][beforeIdx]
          afteridx.remove(minidx)

    # 객체의 수 감소
    elif len(beforeF.index) > len(afterF.index):
        beforeidx = list(range(len(beforeF.index)))
        for afterIdx in range(len(afterF.index)):
            x = afterF['x'][afterIdx]
            y = afterF['y'][afterIdx]
            minidx = -1
            mindis = 999
            for beforeCount in beforeidx:
              dis = distance(x, y, beforeF['x'][beforeCount], beforeF['y'][beforeCount])
              if mindis > dis:
                minidx = beforeCount
                mindis = dis

            afterF['id'][afterIdx] = beforeF['id'][minidx]
            beforeidx.remove(minidx)      


    # 객체의 수 증가    
    else:
        afteridx = list(range(len(afterF.index)))
        for beforeIdx in range(len(beforeF.index)):
            x = beforeF['x'][beforeIdx]
            y = beforeF['y'][beforeIdx]
            minidx = -1
            mindis = 999
            for afterCount in afteridx:
              dis = distance(x, y, afterF['x'][afterCount], afterF['y'][afterCount])
              if mindis > dis:
                minidx = afterCount
                mindis = dis
            afterF['id'][minidx] = beforeF['id'][beforeIdx]
            afteridx.remove(minidx) 

        for i in range(len(afterF.index)):
          if afterF['id'][i] == 'Person':
            afterF['id'][i] = max_id
            max_id += 1

    return_list = [afterF['id'], max_id]
    return return_list


#######################################################################################

start = time.time()

# conver to imgs
toImages(imgs_path, test_video_path)
logging.warning('Finish toImages')

# detection
logging.warning('start detection')
maskRcnn(imgs_path)

# indexing
logging.warning('start load output')
outputs_path = '/content/output/*.txt'
outputs = glob.glob(outputs_path)
outputs =  natsort.natsorted(outputs)

max_id = 0
frame = 0
final_df = pd.DataFrame(columns=['id', 'x', 'y'])
before = pd.DataFrame(columns=['id', 'x', 'y'])

logging.warning('start indexing')
for frame in range(len(outputs)-1):
    before_path = outputs[frame]
    after_path = outputs[frame+1]
    if frame==0:
        before = pd.read_csv(before_path, sep='\t', names = ['id', 'x', 'y'], header=None)
        id_list = np.array(range(1, len(before.index)+1))
        before['id'] = id_list
        max_id = len(before.index)
    
    final_df = final_df.append({'id' : 'frame', 'x' : frame, 'y' : len(before.index)}, ignore_index=True)    
    final_df = final_df.append(before, ignore_index=True)
    
    after = pd.read_csv(after_path, sep='\t', names = ['id', 'x', 'y'], header=None)
    [after['id'], max_id] = objectIndexing(before, after, max_id)
    
    before = after
    
# save final txt file 
final_df = final_df.append({'id' : 'frame', 'x' : (frame+1), 'y' : len(before.index)}, ignore_index=True)    
final_df = final_df.append(before, ignore_index=True)
final_df.to_csv(final_path, sep='\t', header=False, index=False) 


time_min = (time.time()-start)/60
logging.warning(time_min)