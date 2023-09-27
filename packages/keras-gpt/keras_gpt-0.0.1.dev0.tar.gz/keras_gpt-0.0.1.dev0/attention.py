import math
from typing import Optional

import keras_core


def scaled_dot_product_attention(
    query: keras_core.KerasTensor,
    key: keras_core.KerasTensor,
    value: keras_core.KerasTensor,
    mask: Optional[keras_core.KerasTensor] = None,
    return_attention: bool = False,
) -> keras_core.KerasTensor:
    """Computes the scaled dot product attention.

    Note: The input tensors can either have (batch_size, seq_len, model_dim) or
    (batch_size, num_heads, seq_len, model_dim // num_heads) shape.

    Args:
        query: contains the query tensor with shape (..., seq_len, model_dim),
            which is the result of the query linear projection. The query tensor is
            what we want to attend to.
        key: contains the key tensor with shape (..., seq_len, model_dim),
            which is the result of the key linear projection. The key tensor is what
            we use to compute the attention weights.
        value: contains the value tensor with shape (..., seq_len, model_dim),
            which is the result of the value linear projection. The value tensor is
            what we use to compute the context vector.
        mask: contains the mask tensor with shape (..., seq_len, seq_len),
            which is used to avoid the attention mechanism to attend to the
            look-ahead tokens.
        return_attention: if `True` the attention weights will be returned. Defaults to
            `False`.

    Returns:
        The context vector with shape (batch_size, seq_len, model_dim), or a tuple of
        the context vector and the attention weights if `return_attention=True`.
    """
    attention_weights = keras_core.ops.einsum("...qd,...kd->...qk", query, key)
    attention_weights = attention_weights / math.sqrt(query.shape[-1])

    if mask is not None:
        attention_weights = keras_core.ops.where(
            mask == 0, float("-inf"), attention_weights
        )

    attention = keras_core.activations.softmax(attention_weights)

    context_vector = keras_core.ops.matmul(attention, value)
    if return_attention:
        return context_vector, attention
    return context_vector


class SelfAttention(keras_core.layers.Layer):
    r"""Implementation of the `SelfAttention` layer based on the paper
    "Attention is all you need" (https://arxiv.org/pdf/1706.03762.pdf).
    """

    def __init__(self, model_dim: int = 512) -> None:
        super().__init__()

        self.query_dense = keras_core.layers.Dense(units=model_dim)
        self.key_dense = keras_core.layers.Dense(units=model_dim)
        self.value_dense = keras_core.layers.Dense(units=model_dim)

        self.dense_out = keras_core.layers.Dense(units=model_dim)

    def call(
        self,
        x: keras_core.KerasTensor,
        mask: Optional[keras_core.KerasTensor] = None,
    ) -> keras_core.KerasTensor:
        query_proj = self.query_dense(x)
        key_proj = self.key_dense(x)
        value_proj = self.value_dense(x)

        context_vector = scaled_dot_product_attention(
            query_proj, key_proj, value_proj, mask=mask
        )
        return self.dense_out(context_vector)


class MultiHeadAttention(keras_core.layers.Layer):
    """Implementation of the `MultiHeadAttention` layer based on the paper
    "Attention is all you need" (https://arxiv.org/pdf/1706.03762.pdf).
    """

    def __init__(self, model_dim: 512, num_heads: int = 8) -> None:
        super().__init__()

        self.model_dim = model_dim
        self.num_heads = num_heads

        assert model_dim % num_heads == 0

        self.depth = model_dim // num_heads

        self.query_dense = keras_core.layers.Dense(units=model_dim, use_bias=False)
        self.key_dense = keras_core.layers.Dense(units=model_dim, use_bias=False)
        self.value_dense = keras_core.layers.Dense(units=model_dim, use_bias=False)

        self.dense_out = keras_core.layers.Dense(units=model_dim, use_bias=False)

    def split_heads(self, x: keras_core.KerasTensor) -> keras_core.KerasTensor:
        return keras_core.ops.reshape(
            x, (x.shape[0], self.num_heads, x.shape[1], self.depth)
        )

    def call(
        self, x: keras_core.KerasTensor, mask: Optional[keras_core.KerasTensor] = None
    ) -> keras_core.KerasTensor:
        query_proj = self.query_dense(x)
        key_proj = self.key_dense(x)
        value_proj = self.value_dense(x)

        query_proj = self.split_heads(query_proj)
        key_proj = self.split_heads(key_proj)
        value_proj = self.split_heads(value_proj)

        context_vector = scaled_dot_product_attention(
            query_proj, key_proj, value_proj, mask=mask
        )
        context_vector = keras_core.ops.reshape(
            context_vector,
            (context_vector.shape[0], context_vector.shape[2], self.model_dim),
        )
        return self.dense_out(context_vector)
