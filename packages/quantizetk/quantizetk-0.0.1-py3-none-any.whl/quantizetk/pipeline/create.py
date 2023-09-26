from enum import Enum
from pathlib import Path
from typing import Optional, List
from quantizetk.shared.utils.log_util import log
from quantizetk.shared.utils import path_util
from quantizetk.shared.pipeline import (
    Pipeline,
    AutoTokenizer,
    ORTModelForFeatureExtraction,
)
from quantizetk.shared.constants import (
    SAVE_DIR,
    MODEL_FILENAME,
    MODEL_OPTIMIZED_FILENAME,
    MODEL_QUANTIZED_FILENAME,
    OPTIMIZER_CONFIG,
    QUANTIZER_CONFIG,
)


class PipelineID(int, Enum):
    base = 1
    optimized = 2
    quantized = 3


def create_optimized_model(model, config, save_dir):
    from optimum.onnxruntime import ORTOptimizer
    from optimum.onnxruntime.configuration import OptimizationConfig

    optimizer = log(lambda: ORTOptimizer.from_pretrained(model), "loading optimizer")

    optimization_config = OptimizationConfig(**config)
    log(
        lambda: optimizer.optimize(
            save_dir=save_dir,
            optimization_config=optimization_config,
        ),
        "optimizing model",
    )


def create_quantized_model(model, save_dir, config: dict):
    # quantize
    from optimum.onnxruntime import ORTQuantizer
    from optimum.onnxruntime.configuration import AutoQuantizationConfig

    quantizer = log(lambda: ORTQuantizer.from_pretrained(model), "loading quantizer")
    quantization_config = AutoQuantizationConfig.avx512_vnni(**config)
    log(
        lambda: quantizer.quantize(
            save_dir=save_dir,
            quantization_config=quantization_config,
        ),
        "quantizing model",
    )


def load_optimized_pipeline(
    file_name: str,
    save_dir: Path,
    model_id: Optional[str] = None,
    tokenizer: Optional[AutoTokenizer] = None,
):
    if tokenizer is None:
        if not model_id:
            raise ValueError("tokenizer is None and model id is None")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = log(
        lambda: ORTModelForFeatureExtraction.from_pretrained(
            save_dir, file_name=file_name
        ),
        "loading optimized model",
    )
    result = Pipeline(model=model, tokenizer=tokenizer)
    return result


def load_quantized_pipeline(
    model_quantized_filename: str,
    save_dir: Path,
    tokenizer: Optional[AutoTokenizer] = None,
):
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(save_dir)

    model = log(
        lambda: ORTModelForFeatureExtraction.from_pretrained(
            save_dir, file_name=model_quantized_filename
        ),
        "loading quantized model",
    )
    result = Pipeline(model=model, tokenizer=tokenizer)
    return result


def load_base_model(model_id: str, export: bool = True):
    model = log(
        lambda: ORTModelForFeatureExtraction.from_pretrained(model_id, export=export),
        "loading base model",
    )
    return model


def load_base_tokenizer(model_id: str):
    return log(
        lambda: AutoTokenizer.from_pretrained(model_id), "loading base tokenizer"
    )


def load_base_pipeline(model_id: str, save_dir: Path, export: bool = True):
    model = load_base_model(model_id=model_id, export=export)
    log(lambda: model.save_pretrained(save_dir), "saving base model")

    tokenizer = load_base_tokenizer(model_id=model_id)
    log(lambda: tokenizer.save_pretrained(save_dir), "saving base tokenizer")

    pipeline = Pipeline(model=model, tokenizer=tokenizer)
    return pipeline


def validate_pipeline(
    pipeline: Pipeline,
    pipeline_type: PipelineID,
    contents: Optional[List[str]] = None,
):
    message = f"pipeline_validator.{pipeline_type._name_}: "
    if contents:
        vectors = pipeline.get_vectors(contents)
        vectors_length = len(vectors)
        expected_vectors_length = len(contents)
        result = len(vectors) == expected_vectors_length
        if result:
            message += "passed"
        else:
            message += f"failed: {vectors_length} != {expected_vectors_length}"
    else:
        result = True
        message += "passed"
    print(message)
    return result


def create_pipeline(
    model_id: str,
    root_dir: Optional[str] = None,
    save_dir: Optional[Path] = None,
    model_filename: str = MODEL_FILENAME,
    model_optimized_filename: str = MODEL_OPTIMIZED_FILENAME,
    model_quantized_filename: str = MODEL_QUANTIZED_FILENAME,
    optimizer_config: dict = OPTIMIZER_CONFIG,
    quantizer_config: dict = QUANTIZER_CONFIG,
    optimize_model: bool = True,
    quantize_model: bool = True,
):
    save_dir = path_util.get_save_dir(
        save_dir=save_dir, default_save_dir=SAVE_DIR, root_dir=root_dir
    )

    pipeline = load_base_pipeline(model_id=model_id, save_dir=save_dir)

    validate = validate_pipeline(pipeline=pipeline, pipeline_type=PipelineID.base)
    if not validate:
        return

    if optimize_model:
        create_optimized_model(
            model=pipeline.model, config=optimizer_config, save_dir=save_dir
        )

    if quantize_model:
        create_quantized_model(
            model=pipeline.model, save_dir=save_dir, config=quantizer_config
        )

    if optimize_model:
        optimized_pipeline = load_optimized_pipeline(
            file_name=model_optimized_filename,
            save_dir=save_dir,
            tokenizer=pipeline.tokenizer,
        )

        validate = validate_pipeline(
            pipeline=optimized_pipeline, pipeline_type=PipelineID.optimized
        )
        if not validate:
            return

    if quantize_model:
        quantized_pipeline = load_quantized_pipeline(
            model_quantized_filename=model_quantized_filename, save_dir=save_dir
        )
        validate = validate_pipeline(
            pipeline=quantized_pipeline, pipeline_type=PipelineID.quantized
        )
        if not validate:
            return

    model_path = save_dir.joinpath(model_filename)
    path_util.remove_path(model_path)

    optimized_model_path = save_dir.joinpath(model_optimized_filename)
    path_util.remove_path(optimized_model_path)
