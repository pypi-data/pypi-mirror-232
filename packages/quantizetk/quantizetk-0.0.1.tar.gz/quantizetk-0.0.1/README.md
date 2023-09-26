# QuantizeTK

QuantizeTK is a Python library that provides a set of utilities for model optimization and quantization. It simplifies the process of loading optimized and quantized models using OnnxRuntime, along with pre-trained base models. The library is built on top of `transformers` and `optimum`.

## Installation

```bash
pip install quantizetk
```

## Features

- Load optimized, quantized, or base pipelines
- Supports models in the OnnxRuntime ecosystem
- Comprehensive logging and validation utilities
- Configurable optimization and quantization settings

## Quick Start

### Initialize a New Pipeline

```python
from quantizetk import init_pipeline

pipeline = init_pipeline(model_id="your_model_id")
```

### Load an Existing Pipeline

```python
from quantizetk.pipeline.load import load_pipeline

pipeline = load_pipeline()
```

## Directory Structure

```
quantizetk/
│
├── pipeline/
│   ├── create.py
│   ├── load.py
│   └── __init__.py
│
├── shared/
│   ├── constants.py
│   ├── utils/
│   │   ├── validate.py
│   │   └── math_util.py
│   └── __init__.py
│
└── __init__.py
```

## API Overview

### pipeline.create

- `create_pipeline(...)`

### pipeline.load

- `load_pipeline(save_dir, file_name)`

### shared.utils

#### validate

- `validate_pipeline(pipeline, pipeline_type, contents)`

#### math_util

- `normalize(obj, p, dim)`
- `mean_pooling(model_output, attention_mask)`

### shared.constants

- Configuration and path constants

## Contributing

Please read `CONTRIBUTING.md` for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.
