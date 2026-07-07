import cv2
import numpy as np
def process(image_path):
    img=cv2.imread(image_path)
    img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    img=cv2.resive(img,(224,224))
    img=img.astype(np.float32)/255.0
    img=(img-[0.485,0.456,0.406])/[0.229,0.224,0.225]
    return img.transpose(2,0,1)[np.newaxis,...]


    
