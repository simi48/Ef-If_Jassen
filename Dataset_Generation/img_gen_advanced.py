# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# This script generates a set of training data for a playing card recognition
# software. More precisely, it generates a scene of a random amount of randomly 
# augmented random playing cards on a random background (did I mention that 
# it's all random?). It also draws bounding boxes around the images, in order
# to use them in classification.
#
# Author:   Michael Siebenmann
# Date :    11.03.2019
#
# History:
# Version   Date        Who     Changes
# 1.0       11.03.2019  M7ma    created
# 1.1		27.03.2019	M7ma	createScene() function working
# 2.0       11.05.2019  M7ma    complete overhaul:
#                               - better readability
#                               - Parameter card_amount for createScene()
#                                 --> user can specify the amount of cards
#                               and a lot of other fancy stuff
# 2.1       11.05.2019  M7ma    added thumb_fan option
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

def create_txt(idx, cardsYOLO):
    txt_file = open("G:\Informatik_Ergaenzung\\Aufgaben\\Deep_Jass\\Testi\\" + str(idx) + "_scene.txt", "w")
    
    for i in range(len(cardsYOLO)):
        txt_file.write(str(cardsYOLO[i][0]) + " " + str(cardsYOLO[i][1]*0.001) + " " + str(cardsYOLO[i][2]*0.001) 
        + " " + str(cardsYOLO[i][3]*0.001) + " " + str(cardsYOLO[i][4]*0.001) + "\n")

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

def createScene(idx, card_amount, mode):
    transformScene_det = transformScene.to_deterministic()
    
    # load 3 random cards, a random background and a transparent background for superimposing
    bg_file = "D:\Deep_Jass\\Backgrounds\\" + random.choice(os.listdir("D:\Deep_Jass\\Backgrounds"))
    tr_bg = Image.new('RGBA', (1000, 1000), (0, 0, 0, 0))
    background = imageio.imread(bg_file) #read image
    background = np_to_PIL(background).resize((imgW, imgH)) # scale background
    
    classes     = []
    cards       = []
    areas       = []
    rot_angles  = []
    
    angle_dif = 0
    
    for i in range(card_amount):
        classes.append(random.randint(0, 35))                                               # choose random cards
        cards.append(Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(random.randint(1, 2)) 
        + "\\" + str(classes[i]) + ".jpg").convert('RGBA'))                                 # open the corresponding card images
        cards[i] = cards[i].resize((cardW, cardH))                                          # resize card images
        if (mode == "random"):
            areas.append((random.randint(100, 600), (random.randint(100, 600))))            # generate random coordinates for cards
            rot_angles.append(random.randint(0, 359))
        elif (mode == "thumb_fan"):
            points = [(500, 300)]
            points = rotatePoints((imgW/2, imgH/2), points, angle_dif, cards[i])
            areas.append((int(points[0][0]), int(points[0][1])-100))
            rot_angles.append(angle_dif)
            angle_dif += 20
        else:
            print("Invalid mode!")
            exit
                                                   # generate random rotation angles for the cards
        cards[i] = cards[i].rotate(rot_angles[i], expand = 1)                               # rotate the cards
        tr_bg.paste(cards[i], areas[i], cards[i])                                           # paste rotated cards onto image
    
    final = PIL_to_np(tr_bg)
    
    
    keypoints = []
    bbs = []
    cardsYOLO = []
    
    for i in range(card_amount):
        keypoints.append(np.float32([
                (areas[i][0],           areas[i][1]),
                (areas[i][0] + cardW,   areas[i][1]),
                (areas[i][0],           areas[i][1] + cardH),
                (areas[i][0] + cardW,   areas[i][1] + cardH)]))                             # calculate keypoints
            
        keypoints[i] = rotatePoints((areas[i][0] + cardW/2, areas[i][1] + cardH/2), 
                 keypoints[i], rot_angles[i], cards[i])                                     # rotate keypoints
        keypoints[i] = ia.KeypointsOnImage.from_coords_array(keypoints[i], 
                 shape=final.shape)                                                         # convert array to keypointsonimage type
        keypoints[i] = transformScene_det.augment_keypoints(keypoints[i])                   # augment keypoints
        bbs.append(kps_to_BB(keypoints[i]))                                                 # get bounding boxes from keypoints
        cardsYOLO.append((classes[i], (bbs[i].x1+bbs[i].x2)/2, (bbs[i].y1+bbs[i].y2)/2, 
                          abs(bbs[i].x1-bbs[i].x2), abs(bbs[i].y1-bbs[i].y2)))              # generate lists for YOLO, format: 
                                                                                            # [class, x_center, y_center, width, height]
    
    cards_aug = transformScene_det.augment_image(final)
    cards_aug = np_to_PIL(cards_aug)
    
    # paste cards on the random background
    background.paste(cards_aug, (0,0), cards_aug)
    
    final = PIL_to_np(background)
    
    # draw keypoints and bounding boxes on image
#    for i in range(card_amount):
#        final = bbs[i].draw_on_image(final, thickness=3)
#        final = keypoints[i].draw_on_image(final, size=14, color=[255, 0, 255])
        
    display(final)
 
    # generate .txt for YOLOv2
    create_txt(idx, cardsYOLO)
    
    np_to_PIL(final).save("G:\Informatik_Ergaenzung\\Aufgaben\\Deep_Jass\\Testi\\" + str(idx) + '_scene.jpg')

# -----------------------------------------------------------------------------
# Main Program
# -----------------------------------------------------------------------------

# generate scenes
for idx in tqdm(range(10)):
    if random.random() < 0.5:
        createScene(idx, random.randint(3, 9), "thumb_fan")
    else:
        createScene(idx, random.randint(1, 5), "random")
