import os
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
PARENT_DIR=os.path.dirname(BASE_DIR)
ONNX_MODEL_PATH=os.path.join(PARENT_DIR, "models", "mobilenetv2-7.onnx")
LABEL_FILE_PATH=os.path.join(BASE_DIR, "labels.txt")
IMG_MEAN=[0.485, 0.456, 0.406]
IMG_STD=[0.229, 0.224, 0.225]
IMG_SIZE=(224, 224)
INFER_DEVICE="cpu"
CONFIDENCE_THRESHOLD=0.5
if __name__=="__main__":
    import os
    print("模型路径:", ONNX_MODEL_PATH)
    print("模型是否存在:", os.path.exists(ONNX_MODEL_PATH))
    print("标签路径是否存在:", os.path.exists(LABEL_FILE_PATH))