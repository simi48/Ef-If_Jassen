# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# This script modifies textfiles in order to work with YOLOv2
#
# Author:   Michael Siebenmann
# Date :    29.04.2019
#
# History:
# Version   Date        Who     Changes
# 1.0       29.04.2019  M7ma    created
#
# Copyright © Michael Siebenmann, Marc Matter, Simon Thür, Ramon Heeb
# Frauenfeld, Switzerland. All rights reserved
# -----------------------------------------------------------------------------

for idx in range(49431):
    f = open("D:\Deep_Jass\\" + str(idx)+ "_scene.txt", "r")
    lines = f.readlines()
    
    for i in range(3):
        c, x, y, h, w = [int(s) for s in lines[i].split() if s.isdigit()]
        lines[i] = str(c) + " " + str(x/1000) + " " + str(y/1000) + " " + str(h/1000) + " " + str(w/1000) + "\n"
    f.close()
    
    f = open("D:\Deep_Jass\\" + str(idx) + "_scene.txt", "w")
    f.writelines(lines)
    f.close()
