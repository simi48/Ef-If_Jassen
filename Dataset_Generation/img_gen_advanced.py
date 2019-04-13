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
import os
from tqdm import tqdm
import random
import matplotlib.pyplot as plt
from PIL import Image
import math

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
        iaa.SomeOf((3, 7),
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
                
                iaa.GammaContrast((0.5, 1.75), per_channel = True)
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

def create_txt(idx, card1, card2, card3):
    txt_file = open("I:\Informatik_Ergaenzung\\Aufgaben\\Deep_Jass\\Textfiles\\" + str(idx) + "_scene.txt", "w")
       
    txt_file.write(str(card1[0]) + " " + str(card1[1]) + " " + str(card1[2]) + " " + str(card1[3]) + " " + str(card1[4]) + "\n")
    txt_file.write(str(card2[0]) + " " + str(card2[1]) + " " + str(card2[2]) + " " + str(card2[3]) + " " + str(card2[4]) + "\n")
    txt_file.write(str(card3[0]) + " " + str(card3[1]) + " " + str(card3[2]) + " " + str(card3[3]) + " " + str(card3[4]) + "\n")
    txt_file.close()
    
    
    return txt_file

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

# rotate points around given angle, counterclockwise
def rotatePoints(center, points, angle, img):
    angle = math.radians(360-angle)
    width, height = img.size
    rotatedPoints = []
    ox, oy = center
    xoff = (cardW - width)/2
    yoff = (cardH - height)/2
    for i in range(len(points)):
        px, py = points[i]
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy) - xoff
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy) - yoff
        rotatedPoints.append((qx, qy))
    
    rotatedPoints = np.array(rotatedPoints)
    return rotatedPoints

def display(image):
        fig,ax=plt.subplots(1,figsize=(8,8))
        ax.imshow(image)

def createScene(idx):
    transformScene_det = transformScene.to_deterministic()
    
    # load 3 random cards, a random background and a transparent background for superimposing
    bg_file = "D:\Deep_Jass\\Backgrounds\\" + random.choice(os.listdir("D:\Deep_Jass\\Backgrounds"))
    tr_bg = Image.new('RGBA', (1000, 1000), (0, 0, 0, 0))
    background = imageio.imread(bg_file) #read you image
    
    # choose a random card and save it in a variable, so we can pass it to Yolo later
    c1 = random.randint(0, 35)
    c2 = random.randint(0, 35)
    c3 = random.randint(0, 35)
    
    card1 = Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(random.randint(1, 2)) + "\\" + str(c1) + ".jpg").convert('RGBA') #read first random card
    card2 = Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(random.randint(1, 2)) + "\\" + str(c2) + ".jpg").convert('RGBA') #read second random card
    card3 = Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(random.randint(1, 2)) + "\\" + str(c3) + ".jpg").convert('RGBA') #read third random card
    
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
    
    # random angles for rotation
    a = random.randint(0, 359)
    b = random.randint(0, 359)
    c = random.randint(0, 359)
    
    # rotate cards
    card1 = card1.rotate(a, expand = 1)
    card2 = card2.rotate(b, expand = 1)
    card3 = card3.rotate(c, expand = 1)
    
    # superimpose transparent background and the three cards
    tr_bg.paste(card1, area1, card1)
    tr_bg.paste(card2, area2, card2)
    tr_bg.paste(card3, area3, card3)
    
    cards = PIL_to_np(tr_bg)
    
    # create keypoints on images
    keypoints1 = np.float32([
    (x1, y1),
    (x1+cardW, y1),
    (x1, y1+cardH),
    (x1+cardW, y1+cardH)
    ])
    
    keypoints2 = np.float32([
    (x2, y2),
    (x2+cardW, y2),
    (x2, y2+cardH),
    (x2+cardW, y2+cardH)
    ])
    
    keypoints3 = np.float32([
    (x3, y3),
    (x3+cardW, y3),
    (x3, y3+cardH),
    (x3+cardW, y3+cardH)
    ])
    
    # rotate keypoints
    keypoints1 = rotatePoints((x1+cardW/2, y1+cardH/2), keypoints1, a, card1)
    keypoints2 = rotatePoints((x2+cardW/2, y2+cardH/2), keypoints2, b, card2)
    keypoints3 = rotatePoints((x3+cardW/2, y3+cardH/2), keypoints3, c, card3)
    
    # convert array to keypointsonimage type
    keypoints1 = ia.KeypointsOnImage.from_coords_array(keypoints1, shape=cards.shape)
    keypoints2 = ia.KeypointsOnImage.from_coords_array(keypoints2, shape=cards.shape)
    keypoints3 = ia.KeypointsOnImage.from_coords_array(keypoints3, shape=cards.shape)
    
    cards_aug = transformScene_det.augment_image(cards)
    cards_aug = np_to_PIL(cards_aug) # convert back to PIL Image
    
    keypoints1_aug = transformScene_det.augment_keypoints(keypoints1)
    keypoints2_aug = transformScene_det.augment_keypoints(keypoints2)
    keypoints3_aug = transformScene_det.augment_keypoints(keypoints3)
    
    # paste cards on the random background
    background.paste(cards_aug, (0,0), cards_aug)
    
    cards = PIL_to_np(background)
    bb1 = kps_to_BB(keypoints1_aug)
    bb2 = kps_to_BB(keypoints2_aug)
    bb3 = kps_to_BB(keypoints3_aug)
    
    # lists for YOLO, format: [class, x_center, y_center, width, height]
    card1YOLO = [c1, (bb1.x1+bb1.x2)/2, (bb1.y1+bb1.y2)/2, abs(bb1.x1-bb1.x2), abs(bb1.y1-bb1.y2)]
    card2YOLO = [c2, (bb2.x1+bb2.x2)/2, (bb2.y1+bb2.y2)/2, abs(bb2.x1-bb2.x2), abs(bb2.y1-bb2.y2)]
    card3YOLO = [c3, (bb2.x1+bb3.x2)/2, (bb3.y1+bb3.y2)/2, abs(bb3.x1-bb3.x2), abs(bb3.y1-bb3.y2)]
    
    #final = bb1.draw_on_image(cards, thickness=3)
    #final = bb2.draw_on_image(final, thickness=3)
    #final = bb3.draw_on_image(final, thickness=3)
    
    #final = keypoints1_aug.draw_on_image(final, size=14, color=[255, 0, 255])
    #final = keypoints2_aug.draw_on_image(final, size=14, color=[255, 0, 255])
    #final = keypoints3_aug.draw_on_image(final, size=14, color=[255, 0, 255])
    
    #display(cards)
    
    # generate .txt for YOLOv2
    create_txt(idx, card1YOLO, card2YOLO, card3YOLO)
    
    np_to_PIL(cards).save("I:\Informatik_Ergaenzung\\Aufgaben\\Deep_Jass\\Szenen\\" + str(idx) + '_scene.jpg')

# -----------------------------------------------------------------------------
# Main Program
# -----------------------------------------------------------------------------

# generate 5 scenes
for idx in tqdm(range(10000)):
    createScene(idx)
