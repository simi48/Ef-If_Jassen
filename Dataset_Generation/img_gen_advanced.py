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
import pickle
from glob import glob 
from shapely.geometry import Polygon
from PIL import Image

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------

ia.seed(1)

# dimensions of generated images
imgW = 1500
imgH = 1000

# dimensions of a card
cardW = 337
cardH = 526

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
        #
        # Apply the following augmenters to most images.
        #
        #iaa.Fliplr(0.5), # horizontally flip 50% of all images
        iaa.Flipud(0.4), # vertically flip 40% of all images

        # crop some of the images by 0-10% of their height/width
        sometimes(iaa.Crop(percent=(0, 0.1))),

        # Apply affine transformations to some of the images
        # - scale to 80-120% of image height/width (each axis independently)
        # - translate by -20 to +20 relative to height/width (per axis)
        # - rotate by -45 to +45 degrees
        # - shear by -16 to +16 degrees
        # - order: use nearest neighbour or bilinear interpolation (fast)
        # - mode: use any available mode to fill newly created pixels
        #         see API or scikit-image for which modes are available
        # - cval: if the mode is constant, then use a random brightness
        #         for the newly created pixels (e.g. sometimes black,
        #         sometimes white)
        sometimes(iaa.Affine(
            scale={"x": (0.8, 1.2), "y": (0.8, 1.2)},
            translate_percent={"x": (-0.2, 0.2), "y": (-0.2, 0.2)},
            rotate=(-45, 45),
            shear=(-16, 16),
            order=[0, 1],
            cval=(0, 255),
            mode=ia.ALL
        )),

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

                # Search in some images either for all edges or for
                # directed edges. These edges are then marked in a black
                # and white image and overlayed with the original image
                # using an alpha of 0 to 0.7.
                sometimes(iaa.OneOf([
                    iaa.EdgeDetect(alpha=(0, 0.7)),
                    iaa.DirectedEdgeDetect(
                        alpha=(0, 0.7), direction=(0.0, 1.0)
                    ),
                ])),

                # Add gaussian noise to some images.
                # In 50% of these cases, the noise is randomly sampled per
                # channel and pixel.
                # In the other 50% of all cases it is sampled once per
                # pixel (i.e. brightness change).
                iaa.AdditiveGaussianNoise(
                    loc=0, scale=(0.0, 0.05*255), per_channel=0.5
                ),

                # Add a value of -10 to 10 to each pixel.
                #iaa.Add((-10, 10), per_channel=0.5),

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

# to transform 1 card
transformCard = iaa.Sequential([
    iaa.Affine(rotate=(-180,180)),
    iaa.Affine(translate_percent={"x":(-0.25,0.25),"y":(-0.25,0.25)}),
])

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

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

#seq_det = seq.to_deterministic()
# augment keypoints and images
#images_aug = seq_det.augment_images(images)
#keypoints_aug = seq_det.augment_keypoints(keypoints_on_images)

def display(image):
        fig,ax=plt.subplots(1,figsize=(8,8))
        ax.imshow(image)



def createScene():
    background = Image.open("D:\Deep_Jass\\Backgrounds\\banded_0077.jpg") # random background image (using dtd dataset)
    card1 = Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(1) + "\\" + str(random.randint(0, 35)) + ".jpg") #read first random card
    card2 = Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(1) + "\\" + str(random.randint(0, 35)) + ".jpg") #read second random card
    card3 = Image.open("D:\Deep_Jass\\Jasskarten\\Set" + str(1) + "\\" + str(random.randint(0, 35)) + ".jpg") #read third random card
    
    # Scale images to desired values
    background = background.resize((imgW, imgH))
    card1 = card1.resize((cardW, cardH))
    card2 = card2.resize((cardW, cardH))
    card3 = card3.resize((cardW, cardH))

    # superimpose background and the three cards
    area1 = (100, 100)
    area2 = (500, 100)
    area3 = (900, 100)
    background.paste(card1, area1)
    background.paste(card2, area2)
    background.paste(card3, area3)
    
    final = np.array(background)
    
    imageio.imwrite("D:\Deep_Jass\\Testbilder\\" + '_scene.jpg', final)
    display(background)

# -----------------------------------------------------------------------------
# Main Program
# -----------------------------------------------------------------------------

createScene()