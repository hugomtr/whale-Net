import glob 

arr = glob.glob('../imgs/*.jpg')
f = open("imgs_path.txt", "w")
for i in arr:
    f.write(i+"\n")
f.close()
