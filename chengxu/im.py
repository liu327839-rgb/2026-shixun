import cv2
import numpy as np

def bilinear_resize(img, src_h, src_w, dst_h=224, dst_w=224):
    """双线性插值缩放，返回 float32 类型"""
    channels = img.shape[2] if len(img.shape) == 3 else 1
    dst = np.zeros((dst_h, dst_w, channels), dtype=np.float32)
    scale_x = src_w / dst_w
    scale_y = src_h / dst_h

    for c in range(channels):
        for dst_y in range(dst_h):
            for dst_x in range(dst_w):
                # 中心对齐
                src_x = (dst_x + 0.5) * scale_x - 0.5
                src_y = (dst_y + 0.5) * scale_y - 0.5

                # 边界处理
                src_x0 = int(np.floor(src_x))
                src_y0 = int(np.floor(src_y))
                src_x1 = min(src_x0 + 1, src_w - 1)
                src_y1 = min(src_y0 + 1, src_h - 1)

                # 双线性插值（先水平后垂直）
                top = (src_x1 - src_x) * img[src_y0, src_x0, c] + (src_x - src_x0) * img[src_y0, src_x1, c]
                bottom = (src_x1 - src_x) * img[src_y1, src_x0, c] + (src_x - src_x0) * img[src_y1, src_x1, c]
                dst[dst_y, dst_x, c] = (src_y1 - src_y) * top + (src_y - src_y0) * bottom
    return dst

def bgr_to_rgb(img):
    #BGR -> RGB
    dst = np.zeros_like(img)
    dst[..., 0] = img[..., 2]
    dst[..., 1] = img[..., 1]
    dst[..., 2] = img[..., 0]
    return dst
 

def manual_normalize(img):
    """0~255 -> 0~1，向量化"""
    return img.astype(np.float32) / 255.0
    # 若保留循环也可，但向量化更简洁

def manual_standardize(img):
    """均值和标准差标准化，向量化"""
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    return (img - mean) / std

def hwc_to_chw(img):
  
    return np.transpose(img, (2, 0, 1))

def image_process(image_path):
    img = cv2.imread(image_path)           # shape: (H, W, 3) BGR
    h, w = img.shape[:2]
    img = bilinear_resize(img, h, w)       # 缩放至 224x224
    img = bgr_to_rgb(img)                  # BGR -> RGB
    img = manual_normalize(img)            # [0,1]
    img = manual_standardize(img)          # 标准化
    img = hwc_to_chw(img)                  # (3, 224, 224)
    return img[np.newaxis, ...]            # (1, 3, 224, 224)

def image_preprocess_batch(image_paths):
    batch = []
    for path in image_paths:
        batch.append(image_process(path))
    return np.concatenate(batch, axis=0)


    
