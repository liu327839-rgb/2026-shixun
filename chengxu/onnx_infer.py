import os
import onnxruntime as ort
import numpy as np
from config import ONNX_MODEL_PATH, LABEL_FILE_PATH, IMG_MEAN, IMG_STD, IMG_SIZE, INFER_DEVICE, CONFIDENCE_THRESHOLD
def load_labels(label_path:str) ->list:
    label_list = []
    with open(label_path, 'r', encoding='utf-8') as f:
        for line in f:
            clean_line = line.strip()
            if clean_line:
                label_list.append(clean_line)              
    return label_list
def softmax(x:np.ndarray) ->np.ndarray:
    x_max=np.max(x,axis=1,keepdims=True)
    exp_x = np.exp(x-x_max)
    sum_exp_x=np.sum(exp_x,axis=1,keepdims=True)
    return exp_x / sum_exp_x
class OnnxInferEngine:
    def __init__(self):
        if not os.path.exists(ONNX_MODEL_PATH):
            raise FileExistsError(f"模型文件没找到")
        self.session=ort.InferenceSession(ONNX_MODEL_PATH,providers=["CPUExecutionProvider"])
        self.input_name=self.session.get_inputs()[0].name
        self.output_name=self.session.get_outputs()[0].name
        self.labels=load_labels(LABEL_FILE_PATH)
    def predict(self,img_nchw:np.ndarray):
        outputs=self.session.run([self.output_name],{self.input_name:img_nchw})
        logits=outputs[0]
        prob_array=softmax(logits)
        max_index=np.argmax(prob_array,axis=1)[0]
        confidence=float(prob_array[0][max_index])
        if confidence<CONFIDENCE_THRESHOLD:
            return {"class_name":"未知类别","confidence":round(confidence,4)}
        else:
            return{"class_name":self.labels[max_index],"confidence":round(confidence,4)}
if __name__=="__main__":
    engine=OnnxInferEngine()
    test_tensor=np.random.rand(1,3,224,224).astype(np.float32)
    result=engine.predict(test_tensor)
    print("推理测试结果:",result)