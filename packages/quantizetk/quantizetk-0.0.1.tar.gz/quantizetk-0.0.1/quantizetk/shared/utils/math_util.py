import torch as __torch
from torch.nn.functional import normalize as __normalize


def normalize(obj, p: int = 2, dim: int = 1):
    return __normalize(obj, p=p, dim=dim)


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    expanded_attention_mask = attention_mask.unsqueeze(-1)
    token_embeddings_size = token_embeddings.size()
    input_mask_expanded = expanded_attention_mask.expand(token_embeddings_size)
    input_mask_expanded_float = input_mask_expanded.float()

    weighted_sum = __torch.sum(token_embeddings * input_mask_expanded_float, 1)
    mask_sum = __torch.clamp(input_mask_expanded_float.sum(1), min=1e-9)
    mean_pooled = weighted_sum / mask_sum

    return mean_pooled
