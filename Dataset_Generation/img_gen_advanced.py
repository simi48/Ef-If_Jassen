# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# This script generates a set of training data for a playing card recognition
# software. More precisely, it generates a scene of 3 randomly augmented
# random playing cards on a random background. It also draws bounding boxes
# around the images, in order to use them in classification.
#
# Author:   Michael Siebenmann
# Date :    11.03.2019
#
# History:
# Version   Date        Who     Changes
# 1.0       11.03.2019  M7ma    created
# 1.1		27.03.2019	M7ma	createScene() function working
#
# Copyright © Michael Siebenmann, Marc Matter, Simon Thür, Ramon Heeb
# Frauenfeld, Switzerland. All rights reserved
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import imgaug as ia
from imgaug import augmenters as iaa
import numpy as np
import imageio
import cv2
import os
from tqdm import tqdm
import random
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
from matplotlib import cm
from glob import glob 
from PIL import Image

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------

ia.seed(1)

# dimensions of generated images
imgW = 1000
imgH = 1000

# dimensions of a card
cardW = 169
cardH = 263

# center cards in images
decalX = int((imgW - cardW) / 2)
decalY = int((imgH - cardH) / 2)

# keypoints of the bounding box of a whole card
cardKP = ia.KeypointsOnImage([
    ia.Keypoint(x = decalX,       y = decalY),
    ia.Keypoint(x = decalX+cardW, y = decalY),   
    ia.Keypoint(x = decalX+cardW, y = decalY+cardH),
    ia.Keypoint(x = decalX,       y = decalY+cardH)
    ], shape = (imgH, imgW, 3))


xml_body_1="""<annotation>
        <folder>FOLDER</folder>
        <filename>{FILENAME}</filename>
        <path>{PATH}</path>
        <source>
                <database>Unknown</database>
        </source>
        <size>
                <width>{WIDTH}</width>
                <height>{HEIGHT}</height>
                <depth>3</depth>
        </size>
"""
xml_object=""" <object>
                <name>{CLASS}</name>
                <pose>Unspecified</pose>
                <truncated>0</truncated>
                <difficult>0</difficult>
                <bndbox>
                        <xmin>{XMIN}</xmin>
                        <ymin>{YMIN}</ymin>
                        <xmax>{XMAX}</xmax>
                        <ymax>{YMAX}</ymax>
                </bndbox>
        </object>
"""
xml_body_2="""</annotation>        
"""

sometimes = lambda aug: iaa.Sometimes(0.5, aug)

# Define our sequence of augmentation steps that will be applied to a scene of cards
transformScene = iaa.Sequential(
    [
        # Apply affine transformations to some of the images      
        iaa.Affine(
            rotate=(-180, 180),
            shear=(-25, 25),
            order=[0, 1] # - order: use nearest neighbour or bilinear interpolation (fast)
        ),

        #
        # Execute 0 to 5 of the following (less important) augmenters per
        # image. Don't execute all of them, as that would often be way too
        # strong.
        #
        iaa.SomeOf((0, 5),
            [
                # Blur each image with varying strength using
                # gaussian blur (sigma between 0 and 3.0),
                # average/uniform blur (kernel size between 2x2 and 7x7)
                # median blur (kernel size between 3x3 and 11x11).
                iaa.OneOf([
                    iaa.GaussianBlur((0, 3.0)),
                    iaa.AverageBlur(k=(2, 7)),
                    iaa.MedianBlur(k=(3, 11)),
                ]),

                # Sharpen each image, overlay the result with the original
                # image using an alpha between 0 (no sharpening) and 1
                # (full sharpening effect).
                iaa.Sharpen(alpha=(0, 1.0), lightness=(0.75, 1.5)),

                # Same as sharpen, but for an embossing effect.
                iaa.Emboss(alpha=(0, 1.0), strength=(0, 2.0)),


                # Add gaussian noise to some images.
                # In 50% of these cases, the noise is randomly sampled per
                # channel and pixel.
                # In the other 50% of all cases it is sampled once per
                # pixel (i.e. brightness change).
                iaa.AdditiveGaussianNoise(
                    loc=0, scale=(0.0, 0.05*255), per_channel=0.5
                ),

                # Change brightness of images (50-150% of original value).
                iaa.Multiply((0.5, 1.5), per_channel=0.5),

                # Improve or worsen the contrast of images.
                iaa.ContrastNormalization((0.5, 2.0), per_channel=0.5),
            ],
            # do all of the above augmentations in random order
            random_order=True
        )
    ],
    # do all of the above augmentations in random order
    random_order=True
)

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

# convert PIL Image to a numpy array (for augmentation)
def PIL_to_np(img):
    PIL_img = np.array(img)
    return PIL_img

# convert a numpy array to a PIL Image (for superimposing / saving)
def np_to_PIL(img):
    np_img = Image.fromarray(img)
    return np_img

def create_voc_xml(xml_file, img_file,listbba,display=False):
    with open(xml_file,"w") as f:
        f.write(xml_body_1.format(**{'FILENAME':os.path.basename(img_file), 'PATH':img_file,'WIDTH':imgW,'HEIGHT':imgH}))
        for bba in listbba:            
            f.write(xml_object.format(**{'CLASS':bba.classname,'XMIN':bba.x1,'YMIN':bba.y1,'XMAX':bba.x2,'YMAX':bba.y2}))
        f.write(xml_body_2)
        if display: print("New xml", xml_file)

def kps_to_BB(kps):
    extend = 3 # To make the bounding box a bit bigger
    kpsx = [kp.x for kp in kps.keypoints]
    minx = max(0, int(min(kpsx) - extend))
    maxx = min(imgW, int(max(kpsx) + extend))
    kpsy = [kp.y for kp in kps.keypoints]
    miny = max(0, int(min(kpsy) - extend))
    maxy = min(imgH, int(max(kpsy) + extend))
    if minx == maxx or miny == maxy:
        return None
    else:
        return ia.BoundingBox(x1=minx,y1=miny,x2=maxx,y2=maxy)

def display(image):
        fig,ax=plt.subplots(1,figsize=(8,8))
        ax.imshow(image)

def createScene(idx):
    transformScene_det = transformScene.to_deterministic()
    
    # load 3 random cards, a random background and a transparent background for superimposing
    bg_file = "D:\Deep_Jass\\Backgrounds\\" + random.choice(os.listdir("D:\Deep_Jass\\Backgrounds"))
    tr_bg = Image.new('RGBA', (1000, 1000), (0, 0, 0, 0))
    background = imageio.imread(bg_file) #read you image
    card1 = Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(1) + "\\" + str(random.randint(0, 35)) + ".jpg").convert('RGBA') #read first random card
    card2 = Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(1) + "\\" + str(random.randint(0, 35)) + ".jpg").convert('RGBA') #read second random card
    card3 = Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(1) + "\\" + str(random.randint(0, 35)) + ".jpg").convert('RGBA') #read third random card
    
    # Scale images to desired values
    background = np_to_PIL(background).resize((imgW, imgH))
    card1 = card1.resize((cardW, cardH))
    card2 = card2.resize((cardW, cardH))
    card3 = card3.resize((cardW, cardH))
    
    # random coordinates for the cards
    x1 = random.randint(100, 600)
    x2 = random.randint(100, 600)
    x3 = random.randint(100, 600)
    y1 = random.randint(100, 600)
    y2 = random.randint(100, 600)
    y3 = random.randint(100, 600)
    
    area1 = (x1, y1)
    area2 = (x2, y2)
    area3 = (x3, y3)
    
    # rotate cards
    
    # superimpose transparent background and the three cards
    tr_bg.paste(card1, area1, card1)
    tr_bg.paste(card2, area2, card2)
    tr_bg.paste(card3, area3, card3)
    
    cards = PIL_to_np(tr_bg)
    
    # create keypoints on images
    keypoints1 = ia.KeypointsOnImage([
    ia.Keypoint(x=x1, y=y1),
    ia.Keypoint(x=x1+cardW, y=y1),
    ia.Keypoint(x=x1, y=y1+cardH),
    ia.Keypoint(x=x1+cardW, y=y1+cardH)
    ], shape = cards.shape)
    
    keypoints2 = ia.KeypointsOnImage([
    ia.Keypoint(x=x2, y=y2),
    ia.Keypoint(x=x2+cardW, y=y2),
    ia.Keypoint(x=x2, y=y2+cardH),
    ia.Keypoint(x=x2+cardW, y=y2+cardH)
    ], shape = cards.shape)
    
    keypoints3 = ia.KeypointsOnImage([
    ia.Keypoint(x=x3, y=y3),
    ia.Keypoint(x=x3+cardW, y=y3),
    ia.Keypoint(x=x3, y=y3+cardH),
    ia.Keypoint(x=x3+cardW, y=y3+cardH)
    ], shape = cards.shape)
    
    cards_aug = transformScene_det.augment_image(cards)
    keypoints1_aug = transformScene_det.augment_keypoints(keypoints1)
    keypoints2_aug = transformScene_det.augment_keypoints(keypoints2)
    keypoints3_aug = transformScene_det.augment_keypoints(keypoints3)
    cards_aug = np_to_PIL(cards_aug) # convert back to PIL Image
    
    # paste cards on the random background
    background.paste(cards_aug, (0,0), cards_aug)
    
    cards = PIL_to_np(background)
    
    final = keypoints1_aug.draw_on_image(cards, size=10)
    final = keypoints2_aug.draw_on_image(final, size=10)
    final = keypoints3_aug.draw_on_image(final, size=10)
    display(final)
    
    np_to_PIL(final).save("D:\Deep_Jass\\Testbilder\\" + str(idx) + '_scene.jpg')

# -----------------------------------------------------------------------------
# Main Program
# -----------------------------------------------------------------------------

# generate 5 scenes
for idx in tqdm(range(20)):
    createScene(idx)