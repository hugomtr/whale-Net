import numpy as np
import cv2
import matplotlib.pyplot as plt
import re
import os
import json
import sys
import glob


def read_file(filename):
    try:
        f = open(filename, "r")
        dico = json.load(f)
    except:
        print("Could not open train.json")
        return -1

    ## Read all coordinates in json files ##
    coords = dict()
    empty = []
    for i in range(len(dico)):
        path_to_img = dico[i]["filename"]
        number = re.findall("(?<=../imgs/wC\_)(.*)(?=\.jpg)",path_to_img).pop()
        if path_to_img:
            if len(dico[i]['objects']) == 2:
                coords[int(number)] = dict()
                if dico[i]['objects'][0]['name'] == 'head':
                    coords[int(number)]["head"] = [dico[i]['objects'][0]["relative_coordinates"]["center_x"],dico[i]['objects'][0]["relative_coordinates"]["center_y"]]
                    coords[int(number)]["air"] = [dico[i]['objects'][1]["relative_coordinates"]["center_x"],dico[i]['objects'][1]["relative_coordinates"]["center_y"]]
                else:
                    coords[int(number)]["head"] = [dico[i]['objects'][1]["relative_coordinates"]["center_x"],dico[i]['objects'][1]["relative_coordinates"]["center_y"]]
                    coords[int(number)]["air"] = [dico[i]['objects'][0]["relative_coordinates"]["center_x"],dico[i]['objects'][0]["relative_coordinates"]["center_y"]]

            else:
                empty.append(number)
    empty = " ".join(empty)
    with open("empty.txt","w") as f:
        f.write(empty)
    return coords


## some helper function ##
def find_angle(coords,c,transpose = False):
    if transpose:
        print("transpose")
        x1,y1 = coords[c]["head"][1],coords[c]["head"][0]
        x2,y2 = coords[c]["air"][1],coords[c]["air"][0]
    else:
        x1,y1 = coords[c]["head"][0],coords[c]["head"][1]
        print(coords[c]["head"][0],coords[c]["head"][0])
        x2,y2 = coords[c]["air"][0],coords[c]["air"][1]
    a = x1 - x2
    b = y1 - y2
    r = np.sqrt(a*a + b*b)

    if a >= 0 and b <= 0:
        alpha = 360 - np.arccos(a/r)*(180/np.pi) 
    if a <= 0 and b <= 0:
        alpha = 270 - np.arccos(np.abs(b)/r)*(180/np.pi) 
    if a <= 0 and b >= 0:
        alpha = 90 + np.arccos(np.abs(b)/r)*(180/np.pi) 
    if a >= 0 and b >= 0:
        alpha = np.arccos(a/r)*(180/np.pi)
    return alpha


def crop_rotated(rotated_img):
    i=0
    h,w = rotated_img.shape[0],rotated_img.shape[1]
    while len(rotated_img[rotated_img == 0]) > 10:
        i+=1
        h_new,w_new = int(h*0.99),int(w*0.99) 
        x,y = h - h_new,w - w_new
        a,b = int(x/2),int(h-x/2)
        c,d = int(y/2),int(w-y/2)
        rotated_img = rotated_img[a:b,c:d]
        h,w = rotated_img.shape[0],rotated_img.shape[1]
    return rotated_img

    
def crop_rotated(rotated_img):
    i=0
    w,h = rotated_img.shape[0],rotated_img.shape[1]
    #ratio = h/w
    while len(rotated_img[rotated_img == 0]) > 10:
        i+=1
        h,w = rotated_img.shape[0],rotated_img.shape[1]
        x,y = max(1,int(h*0.01)),max(1,int(w*0.01))  
        #print(x,y)
        rotated_img = rotated_img[x:-x,y:-y] 
        #print("ratio",ratio)
    return rotated_img


def main():
    if len(sys.argv) != 3:
        print("Utilisation: python3 resize_alignemnet file_with_coords.json image_folder_path")
    try:
        coords = read_file(str(sys.argv[1]))
        source_dir = str(sys.argv[2])
    except:
        quit()    
    img_index = np.array(list(coords.keys())).astype("int")
    path = lambda num : source_dir + "/wC_" + str(num) + ".jpg"

    ###########################
    # Distribution du dataset #
    ###########################
    # print("starting distributons of dataset displays")

    # shapes = []
    # for i in img_index:
    #     img = cv2.imread(path(i),cv2.IMREAD_COLOR)
    #     shapes.append(list(img.shape))
    # shapes = np.array(shapes)  

    # fig = plt.figure()
    # ax1 = fig.add_subplot(121)
    # ax2 = fig.add_subplot(122)
    # ax1.hist(shapes[:,0],bins=100)
    # ax2.hist(shapes[:,1],bins=100)
    # ax1.title.set_text("hauteur pixels image")
    # ax2.title.set_text("largeur pixels image")
    # print("saving dimensions of dataset in .png file")
    # plt.savefig('foo.png')
    print("starting to resize and align images")
     
    #############################################
    # Début du resize et alignements des images #
    #############################################


    ###  Images avec alignement dans le json  ###
    
    try:
        os.makedirs("imgs_align")
    except:
        pass

    counter = 0
    for c in img_index:
        img = cv2.imread(path(c),cv2.IMREAD_COLOR)
        #img = img[:,:,::-1]
        transpose = False
        if img.shape[0] > img.shape[1]:
            img = cv2.transpose(img)
            transpose = True

        height, width = img.shape[:2]
        center = (width/2, height/2) 
        angle = find_angle(coords,c,transpose)
        rotate_matrix = cv2.getRotationMatrix2D(center=center, angle=angle, scale=1)

        # rotate the image using cv2.warpAffine
        rotated_image = cv2.warpAffine(src=img, M=rotate_matrix, dsize=(width, height))

        crop_rotated_img = crop_rotated(rotated_image)
        
        counter +=1
        left = len(img_index) - counter 
        crop_rotated_img = cv2.transpose(crop_rotated_img)

        print("Image wCR_" + str(c) + ".jpg created "+ str(left) + " image(s) left")
        
        cv2.imwrite("imgs_align/wCR_"+ str(c) + ".jpg",crop_rotated_img)

    ###  Strating to take care of images without labelization in the json file ###


if __name__ == "__main__":
    main()


