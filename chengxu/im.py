import cv2
import numpy as np
def bilinear_resize(img,src_h,src_w,dst_h=224,dst_w=224):#scr:原图,dst:目标图
   channels = img.shape[2] if len(img.shape) == 3 else 1 #判断是否为彩色图
   dst=np.zeros((dst_h,dst_w,channels),dtype=np.float32)
   scale_x = src_w/dst_w
   scale_y = src_h/dst_h
   for c in range(channels):
     for dst_x in range(dst_w):
       for dst_y in range(dst_h):
         src_x = (dst_x+0.5)*scale_x-0.5
         src_y = (dst_y+0.5)*scale_y-0.5
         #源图上临近点位置
         src_x0 = int(np.floor(src_x))   
         src_y0 = int(np.floor(src_y))
         src_x1 = min(src_x0 + 1,src_w - 1)
         src_y1 = min(src_y0 + 1,src_h - 1)
         top = (src_x1 - src_x) * img[src_y0,src_x0,c] + (src_x - src_x0) * img[src_y0,src_x1,c]
         bottom = (src_x1 - src_x) * img[src_y1,src_x0,c] + (src_x - src_x0) * img[src_y1,src_x1,c]
         dst[dst_y,dst_x,c] = ((src_y1-src_y)*top+(src_y-src_y0)*bottom)
   return dst
                                
def bgr_to_rgb(img):
    dst = np.zeros_like(img)
    h,w,c=img.shape
    for i in range(h):
      for j in range(w):
         dst[i,j,2] = img[i,j,0]
         dst[i,j,1] = img[i,j,1]
         dst[i,j,0] = img[i,j,2]
    return dst
def manual_normalize(img):#0~225转为0~1
   h,w,c = img.shape
   dst = np.zeros_like(img,dtype=np.float32)
   for i in range (h):
      for j in range (w):
         for ch in range (c):
            dst[i,j,ch] = img[i,j,ch]/255.0
   return dst
def manual_standardize(img):#标准化
   mean = np.array([0.485,0.456,0.406],dtype=np.float32)
   std = np.array([0.229,0.224,0.225],dtype=np.float32)
   h,w,c = img.shape
   dst = np.zeros_like(img,dtype=np.float32)
   for i in range (h):
      for j in range (w):
         for ch in range (c):
            dst[i,j,ch]=(img[i,j,ch]-mean[ch])/std[ch]
   return dst
def hwc_to_chw(img):#重排
   h,w,c = img.shape
   dst = np.zeros_like(img,dtype=np.float32)
   for i in range (h):
      for j in range (w):
         for ch in range (c):
            dst[ch,i,j,] = img[i,j,ch]
   return dst

   


def image_process(image_path):
    img=cv2.imread(image_path)
    #img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    #img=cv2.resize(img,(224,224))

    #img=img.astype(np.float32)/255.0
    #img=(img-[0.485,0.456,0.406])/[0.229,0.224,0.225]
    img = bilinear_resize(img)
    img = bgr_to_rgb(img)
    img = manual_normalize(img)
    img = manual_standardize(img)
    img = hwc_to_chw(img)

    return img.transpose(2,0,1)[np.newaxis,...]


def image_preprocess_batch(image_path):
   batch = []
   for path in image_path:
      img =  image_process(path)
      batch.append(img)
   return np.concatenate(batch,axis=0)



    
