import torch

class Attention(torch.autograd.Function):
    @staticmethod
    @torch.no_grad()
    def forward(ctx, q, k, v, sm_scale=None, causal=True, tile_size=None):
        if sm_scale is None:
            sm_scale = q.shape[-1] ** -0.5
        B, H, L, D = q.shape
        if tile_size is None:
            tile_size = L
        outputs = torch.zeros_like(q)
        i_coords = torch.linspace(0, L - 1, L).unsqueeze(-1).to(q)
        j_coords = torch.linspace(0, L - 1, L).unsqueeze(0).to(q)
        sums = torch.zeros(B, H, L).to(q)
        for i in range(0, L, tile_size):
            q_tile = q[:, :, i:i+tile_size, :]
            scores = (q_tile @ k.transpose(-1, -2)) * sm_scale
            if causal:
                mask = (i_coords[i:i+tile_size] >= j_coords).unsqueeze(0).unsqueeze(0)
                scores = torch.where(mask[None, None], scores, 0)
            sums[:, :, i:i+tile_size] += scores.sum(-1)
            outputs[:, :, i:i+tile_size] += scores @ v
        outputs /= sums[..., None]
        ctx.save_for_backward(q, k, v, outputs, sums)
        ctx.causal = causal
        ctx.tile_size = tile_size
        return outputs, sums

    @staticmethod
    @torch.no_grad()
    def backward(ctx, do, dsums):
        q, k, v, output, sums = ctx.saved_tensors
        causal = ctx.causal
        tile_size = ctx.tile_size
        B, H, L, D = q.shape
        if tile_size is None:
            tile_size = L
        dQ = torch.zeros_like(q)
        dK = torch.zeros_like(k) 
        dV = torch.zeros_like(v)
        i_coords = torch.linspace(0, L - 1, L).unsqueeze(-1).to(q)
        j_coords = torch.linspace(0, L - 1, L).unsqueeze(0).to(q)
        delta = (do * output).sum(-1)
        for i in range(0, L, tile_size):
            q_tile = q[:, :, i:i+tile_size, :]
            delta_tile = delta[:, :, i:i+tile_size]
            do_tile = do[:, :, i:i+tile_size, :]
            s = (q_tile @ k.transpose(-1, -2)) * q.shape[-1] ** -0.5
            s /= sums[:, :, i:i+tile_size, None]
            if causal:
                mask = (i_coords[i:i+tile_size] >= j_coords).unsqueeze(0).unsqueeze(0)
                s = torch.where(mask, s, 0)
            dP = do_tile @ v.transpose(-1, -2)
            dS = (dP - delta_tile[..., None]) / sums[:, :, i:i+tile_size, None] * q.shape[-1] ** -0.5
            if causal:
                dS = torch.where(mask, dS, 0)
            dV += s.transpose(-1, -2) @ do_tile
            dQ[:, :, i:i+tile_size, :] += dS @ k
            dK += (q_tile.transpose(-1, -2) @ dS).transpose(-1, -2)
        return dQ, dK, dV, None, None, None

low_mem_attn = Attention.apply
