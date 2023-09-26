SAVE_DIR = "storage/onnx"
MODEL_FILENAME = "model.onnx"
MODEL_OPTIMIZED_FILENAME = "model_optimized.onnx"
MODEL_QUANTIZED_FILENAME = "model_quantized.onnx"
TOKENIZER_CONFIG = dict(padding=True, truncation=True, return_tensors="pt")
OPTIMIZER_CONFIG = dict(optimization_level=99)
QUANTIZER_CONFIG = dict(is_static=False, per_channel=False)
