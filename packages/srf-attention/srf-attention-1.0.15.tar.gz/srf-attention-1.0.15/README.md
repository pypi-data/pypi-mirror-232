# srf-attention
Simplex Random Feature attention, in PyTorch

## A Prelude
### Why?
Softmax attention ate the world. But now it's eating our wallets. Luckily enough for us wordcels, those nifty shape rotators realized that even though softmax isn't :wave: technically :wave: stationary, it's amenable to Monte Carlo methods. Translation: we can retrofit pretrained LLMs for recurrent inference! Smarter men than I proceeded to publish [this](https://arxiv.org/abs/2009.14794), [this](https://arxiv.org/abs/2205.15317), and [that](https://arxiv.org/abs/2301.13856). This repo is a PyTorch implementation of "that", with some syntactic sugar added to aid digestion. It's intended to be used for [ERPTRI](https://github.com/alexjlevenston/erptri-train), but do with it what you will.

### What is this good for?
Well, it really ain't for you open-sourcerers. You're bottlenecked by weight I/O. But for those running large-batch inference, e.g as part of a data pipeline, KV cache I/O is the limiter for sequences > ~700 tokens. [ERPTRI](https://github.com/alexjlevenston/erptri-train) efficiently [sic] drops the KV cache size of any pretrained auto-regressive Transformer from $`O(LD)`$ to $`O(D^2)`$. This repo implements the PyTorch modules necessary for the fine-tuning phase of ERPTRI, and for efficient inference.

### Next steps
Venture forth and conquer.

## Installation
```bash
pip install git+https://github.com/alexjlevenston/srf-attention
```

## Usage
```python
import torch
from srf_attention import FastAttention, simplex_random_matrix

device = 'cpu'

B, H, L, D = (1, 8, 1024, 128)

# Generate some simplex random features
srfs = simplex_random_matrix(nb_rows = D, nb_features = D, normalize = False, device = device)

# Or just use the FastAttention module
attn = FastAttention(head_dim = D, nb_features = D, causal = True).to(device)
# For training, automatically redraw features for each forward pass
# False by default
attn.redraw_on_call_(True)

# Placeholder queries, keys, and values:
q, k, v = [torch.empty(B, H, L, D) for _ in range(3)]

# For training, naive torch:
o = attn(q=q, k=k, v=v, mode='train', attn_fn='torch')
# For training, w/ flash-attention-no-softmax:
o = attn(q=q, k=k, v=v, mode='train', attn_fn='flash')

# For inference, disable auto-redraw:
attn.redraw_on_call_(False)
# For inference, prefill, parallel:
o, kv, key_maxima, denominator = (q=q, k=k, v=v, mode='prefill', attn_fn='parallel')
# For inference, prefill, chunkwise-recurrent:
o, kv, key_maxima, denominator = (q=q, k=k, v=v, mode='prefill', attn_fn='chunkwise-recurrent')
# For inference, prefill, recurrent:
o, kv, key_maxima, denominator = (q=q, k=k, v=v, mode='prefill', attn_fn='recurrent')
# For inference, generation:
q = torch.empty(B, H, 1, D)
denominator = torch.empty(B, H, 1, D)
o, kv, key_maxima, denominator = (q=q, kv=kv, key_maxima=key_maxima, denominator=denominator, mode='generation')

```
