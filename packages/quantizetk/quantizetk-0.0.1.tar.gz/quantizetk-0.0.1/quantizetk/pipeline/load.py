from typing import Optional
from quantizetk.shared.pipeline import Pipeline
from quantizetk.shared.utils import path_util
from quantizetk.shared.constants import SAVE_DIR


def load_pipeline(
    save_dir: str = SAVE_DIR, file_name: Optional[str] = None
) -> Pipeline:
    if not file_name:
        model_paths = path_util.get_dirpaths(save_dir, "onnx")
        file_name = path_util.filename(model_paths[0])

    model = Pipeline.Model.from_pretrained(save_dir, file_name=file_name)
    tokenizer = Pipeline.Tokenizer.from_pretrained(save_dir)

    result = Pipeline(model=model, tokenizer=tokenizer)
    return result
