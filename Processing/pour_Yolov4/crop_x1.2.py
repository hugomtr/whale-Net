import glob
import re
import numpy as np
import cv2
import os

# folder source (où sont les images)
source_dir = ''
# folder où stocker les images cropper
target_dir = ''

os.chdir(source_dir)
all_txt_names = glob.glob("w_*.txt")
all_jpg_names = glob.glob("w_*.jpg")
all_txt_names = " ".join(all_txt_names)
all_jpg_names = " ".join(all_jpg_names)

for i in range(0,11469):
    if i == 7489:
        continue
    path_to_file = re.findall("(w\_" + str(i) + "\.txt)",all_txt_names).pop()
    path_to_img = re.findall("(w\_" + str(i) + "\.jpg)",all_jpg_names).pop()
    line = [line.rstrip() for line in open(path_to_file)].pop()
    line = np.array(str(line).split(" "))
    box_coords = line[1:].astype('float32')

    img = cv2.imread(path_to_img)
    shape = img.shape 

    w = int(shape[1]*box_coords[2])    
    h = int(shape[0]*box_coords[3])
    center_col = int(shape[1]*box_coords[0])
    center_lin = int(shape[0]*box_coords[1])

    x = int(center_lin - h/2)
    y = int(center_col - w/2)

    x1 = max(0,int(x - h/10))
    x2 = min(img.shape[0],x+h+2*int(h/10))
    y1 = max(0,int(y - w/10))
    y2 = min(img.shape[1],y+w+2*int(w/10))
    cropped_image = img[x1:x2,y1:y2]

    print(i,path_to_file,path_to_img)

    name = "wC_" + str(i) + ".jpg"
    cv2.imwrite(target_dir + name, cropped_image)

