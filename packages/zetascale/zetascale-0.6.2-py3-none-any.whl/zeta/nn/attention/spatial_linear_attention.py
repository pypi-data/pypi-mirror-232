# import torch
# import torch.nn as nn

# from einops import rearrange

# from einops_exts import check_shape, rearrange_many


# class SpatialLinearAttention(nn.Module):
#     def __init__(self,
#                  dim: int = None,
#                  heads: int = 4,
#                  dim_head: int = 32):
#         super().__init__()
#         self.scale = dim_head ** -0.5
#         self.heads = heads
#         hidden_dim = dim_head * heads

#         self.to_qkv = nn.Conv2d(dim,
#                                 hidden_dim * 3,
#                                 1,
#                                 bias=False)
#         self.to_out = nn.Conv2d(hidden_dim,
#                                 dim,
#                                 1)
        
#     def forward(self, x):
#         b, c, f, h, w = x.shape
#         x = rearrange(x, 'b c f h w -> (b f) c h w')

#         qkv = self.to_qkv(x).chunk(3, dim=1)
#         q, k, v = rearrange_many(qkv, 'b (h c) x y -> b h c (x y)', h = self.heads)

#         q = q.softmax(dim=-2)
#         k = k.softmax(dim=-1)

#         q = q * self.scale
#         context = torch.einsum('b h d n, b h e n -> b h d e', k, v)

#         out = torch.einsum('b h d e, b h d n -> b h e n', context, q)
#         out = rearrange(out, 'b h c (x y) -> b (h c) x y', h=self.heads, x=h, y=w)
#         out = self.to_out(out)
        
#         return rearrange(out, '(b f) c h w -> b c f h w', b=b)
    

# class EinopsToAndFrom(nn.Module):
#     def __init_(self, from_einops, to_einops, fn):
#         super().__init__()
#         self.from_einops = from_einops
#         self.to_einops = to_einops
#         self.fn = fn
    
#     def forward(self, x, **kwargs):
#         shape = x.shape
#         reconstruction_kwargs = dict(tuple(zip(self.from_einops.split(' '), shape)))
#         x = rearrange(x, f'{self.from_einops} -> {self.to_einops}')
#         x = self.fn(x, **kwargs)
#         x = rearrange(x, f"{self.to_einops} -> {self.from_einops}", **reconstitue_kwargs)
