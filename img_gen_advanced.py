# -*- coding: utf-8 -*-


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

ia.seed(1)

# Example batch of images.
# The array has shape (32, 64, 64, 3) and dtype uint8.
#images = np.array(
#    [img for _ in range(32)], dtype=np.uint8)  # 32 means create 32 enhanced images using following methods.

# dimensions of generated images
imgW = 1000
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

def create_voc_xml(xml_file, img_file,listbba,display=False):
    with open(xml_file,"w") as f:
        f.write(xml_body_1.format(**{'FILENAME':os.path.basename(img_file), 'PATH':img_file,'WIDTH':imgW,'HEIGHT':imgH}))
        for bba in listbba:            
            f.write(xml_object.format(**{'CLASS':bba.classname,'XMIN':bba.x1,'YMIN':bba.y1,'XMAX':bba.x2,'YMAX':bba.y2}))
        f.write(xml_body_2)
        if display: print("New xml",xml_file)

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

#seq_det = seq.to_deterministic() # call this for each batch again, NOT only once at the start
# augment keypoints and images
#images_aug = seq_det.augment_images(images)
#keypoints_aug = seq_det.augment_keypoints(keypoints_on_images)

def display(image):
        fig,ax=plt.subplots(1,figsize=(8,8))
        ax.imshow(image)

# Scale Images
scaleBackground = iaa.Scale({"height": imgH, "width": imgW})
scaleCard       = iaa.Scale({"height": cardH, "width": cardW})

def createScene():
    background = imageio.imread("D:\Deep_Jass\\Backgrounds\\banded_0077.jpg") # random background image (using dtd dataset)
    card1 = imageio.imread("D:\Deep_Jass\\Jasskarten\\Set" + str(1) + "\\" + str(random.randint(0, 35)) + ".jpg") #read first random card
    card2 = imageio.imread("D:\Deep_Jass\\Jasskarten\\Set" + str(1) + "\\" + str(random.randint(0, 35)) + ".jpg") #read second random card
    card3 = imageio.imread("D:\Deep_Jass\\Jasskarten\\Set" + str(1) + "\\" + str(random.randint(0, 35)) + ".jpg") #read third random card
    
    card1 = np.zeros((imgH, imgW, 4), dtype = np.uint8)
    card2 = np.zeros((imgH, imgW, 4), dtype = np.uint8)
    card3 = np.zeros((imgH, imgW, 4), dtype = np.uint8)
    
    background = scaleBackground.augment_image(background)
    card1 = scaleCard.augment_image(card1)
    card2 = scaleCard.augment_image(card2)
    card3 = scaleCard.augment_image(card3)
    
    # superimpose background and the three cards
    mask1 = card1[:,:,3]
    mask1 = np.stack([mask1]*3,-1)
    final = np.where(mask1,card1[:,:,0:3], background)
    mask2 = card2[:,:,3]
    mask2 = np.stack([mask2]*3,-1)
    final = np.where(mask2, card2[:,:,0:3], final)
    mask3 = card3[:,:,3]
    mask3 = np.stack([mask3]*3,-1)
    final = np.where(mask3, card3[:,:,0:3], final)
    
    imageio.imwrite("D:\Deep_Jass\\Testbilder\\" + '_scene.jpg', final)
    display(card1)

createScene()

#for img_idx, (image_after, keypoints_after) in enumerate(zip(images_aug, keypoints_aug)):
    #bb_aug = kps_to_BB(keypoints_after)
    #image_after = bb_aug.draw_on_image(image_after, thickness=2)
    #imageio.imwrite("D:\Deep_Jass\\Testbilder\\" + str(img_idx)+'marc.jpg', image_after)