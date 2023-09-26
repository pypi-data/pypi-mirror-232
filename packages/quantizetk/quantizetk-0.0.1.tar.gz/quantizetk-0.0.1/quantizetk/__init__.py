from typing import Optional
from pathlib import Path
from quantizetk.shared.pipeline import Pipeline
from quantizetk.pipeline.load import load_pipeline
from quantizetk.pipeline.create import create_pipeline
from quantizetk.shared.constants import (
    MODEL_FILENAME,
    MODEL_OPTIMIZED_FILENAME,
    MODEL_QUANTIZED_FILENAME,
    OPTIMIZER_CONFIG,
    QUANTIZER_CONFIG,
)


def init_pipeline(
    model_id: str,
    root_dir: Optional[str] = None,
    save_dir: Optional[Path] = None,
    file_name: Optional[str] = None,
    model_filename: str = MODEL_FILENAME,
    model_optimized_filename: str = MODEL_OPTIMIZED_FILENAME,
    model_quantized_filename: str = MODEL_QUANTIZED_FILENAME,
    optimizer_config: dict = OPTIMIZER_CONFIG,
    quantizer_config: dict = QUANTIZER_CONFIG,
    optimize_model: bool = True,
    quantize_model: bool = True,
) -> Pipeline:
    pipeline = None
    try:
        pipeline = load_pipeline(save_dir=save_dir, file_name=file_name)
    except BaseException as error:
        print(f"load pipeline failed; creating pipeline")
        create_pipeline(
            model_id=model_id,
            root_dir=root_dir,
            save_dir=save_dir,
            model_filename=model_filename,
            model_optimized_filename=model_optimized_filename,
            model_quantized_filename=model_quantized_filename,
            optimizer_config=optimizer_config,
            quantizer_config=quantizer_config,
            optimize_model=optimize_model,
            quantize_model=quantize_model,
        )
    if pipeline is None:
        print("attempting to load newly created model")
        pipeline = load_pipeline(save_dir=save_dir, file_name=file_name)
    return pipeline
