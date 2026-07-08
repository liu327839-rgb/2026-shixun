import onnxruntime as ort
import numpy as np

class ONNXInfer:
    def __init__(self, model_file_path, use_gpu=False):
        # 设置推理执行硬件
        self.providers = []
        if use_gpu:
            self.providers.append("CUDAExecutionProvider")
        self.providers.append("CPUExecutionProvider")
        # 加载onnx模型会话
        self.sess = ort.InferenceSession(model_file_path, providers=self.providers)
        # 预存输入输出名称，外部直接调用
        self.input_names = [i.name for i in self.sess.get_inputs()]
        self.output_names = [o.name for o in self.sess.get_outputs()]
        self.input_shapes = [i.shape for i in self.sess.get_inputs()]
        self.input_dtypes = [i.type for i in self.sess.get_inputs()]
        print("======== ONNX模型加载成功 ========")
        print(f"输入节点名称：{self.input_names}")
        print(f"输入节点尺寸：{self.input_shapes}")
        print(f"输出节点名称：{self.output_names}")

    def run_infer(self, input_data_dict):
        """
        推理主接口
        :param input_data_dict: 字典，key=输入节点名，value=队友预处理好的np.float32数组
        :return: list，按模型输出顺序存放所有推理结果ndarray
        """
        # 统一转float32，防止队友传错数据类型报错
        fixed_input = {}
        for name, arr in input_data_dict.items():
            fixed_input[name] = arr.astype(np.float32)
        # 执行推理
        outputs = self.sess.run(self.output_names, fixed_input)
        return outputs

# 测试入口，正式项目使用时删掉下面if __name__块即可
if __name__ == "__main__":
    # 1. 初始化模型，替换成你的onnx真实路径
    model = ONNXInfer(model_file_path=r"./model.onnx", use_gpu=False)

    # 2. 模拟队友预处理完成的数据，按模型输入shape生成随机数组
    # 如果是多输入模型，在字典内新增键值对即可
    fake_input_array = np.random.randn(*model.input_shapes[0]).astype(np.float32)
    input_package = {
        model.input_names[0]: fake_input_array
    }

    # 3. 执行推理
    infer_result = model.run_infer(input_package)

    # 4. 打印输出信息给队友对接
    print("\n======== 推理输出信息 ========")
    for idx, out_arr in enumerate(infer_result):
        print(f"输出{idx} shape: {out_arr.shape}")
        print(f"输出{idx} 前5个数据：{out_arr.flatten()[:5]}")