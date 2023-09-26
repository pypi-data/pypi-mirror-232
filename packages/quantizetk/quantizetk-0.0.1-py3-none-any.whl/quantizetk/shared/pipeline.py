from transformers import AutoTokenizer, Pipeline as AutoPipeline
from optimum.onnxruntime import ORTModelForFeatureExtraction
from .utils import math_util
from .constants import TOKENIZER_CONFIG


class Pipeline(AutoPipeline):
    Model = ORTModelForFeatureExtraction
    Tokenizer = AutoTokenizer

    def _sanitize_parameters(self, **kwargs):
        preprocess_kwargs = {}
        return preprocess_kwargs, {}, {}

    def preprocess(self, inputs):
        return self.tokenizer(inputs, **TOKENIZER_CONFIG)

    def _forward(self, model_inputs):
        outputs = self.model(**model_inputs)
        return {"outputs": outputs, "attention_mask": model_inputs["attention_mask"]}

    def postprocess(self, model_outputs):
        data = math_util.mean_pooling(
            model_outputs["outputs"], model_outputs["attention_mask"]
        )
        return math_util.normalize(data)

    def get_vectors(self, contents: list[str]):
        return self(contents)

    def get_vector(self, content: str):
        vectors = self.get_vectors([content])
        return vectors[0]
