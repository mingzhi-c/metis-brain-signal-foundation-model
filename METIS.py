import torch
import torch.nn as nn
import math
import torch.nn.functional as F
from einops import rearrange
from dataclasses import dataclass

@dataclass
class MetisConfig:
    dim: int = 512
    hidden_dim: int = 2048
    n_layers: int = 12
    head_dim: int = 64
    num_key_value_heads: int = 2
    signal_rope_base: float = 10000
    text_rope_base: float = 100000
    max_signal_seq_len: int = 512
    max_text_seq_len: int = 512
    vocab_size: int = 151936
    num_classes: int = 5

class Gate(nn.Module):
    def __init__(self, dim, topk=2, n_routed_experts=8):
        super().__init__()
        self.dim = dim
        self.topk = topk
        self.n_routed_experts = n_routed_experts
        self.score_func = "softmax"
        self.route_scale = 1
        self.weight = nn.Parameter(torch.empty(n_routed_experts, dim))
        self.bias = nn.Parameter(torch.empty(n_routed_experts))
        self.alpha = 0.0001

    def forward(self, x):
        scores = F.linear(x, self.weight)
        if self.score_func == "softmax":
            scores = scores.softmax(dim=-1, dtype=torch.float32)
        else:
            scores = scores.sigmoid()
        original_scores = scores
        scores = scores + self.bias
        indices = torch.topk(scores, self.topk, dim=-1)[1]
        weights = original_scores.gather(1, indices)
        if self.score_func == "sigmoid":
            weights /= weights.sum(dim=-1, keepdim=True)
        weights *= self.route_scale
        if self.training and self.alpha > 0:
            mask_ce = F.one_hot(indices.view(-1), num_classes=self.n_routed_experts)
            ce = mask_ce.float().mean(0)
            Pi = original_scores.mean(0)
            fi = ce * self.n_routed_experts
            aux_loss = (Pi * fi).sum() * self.alpha
        else:
            aux_loss = x.new_tensor(0.0)
        return weights.type_as(x), indices, aux_loss


class MLP(nn.Module):
    def __init__(self, dim, hidden_dim):
        super().__init__()
        self.gate_proj = nn.Linear(dim, hidden_dim, bias=False)
        self.up_proj = nn.Linear(dim, hidden_dim, bias=False)
        self.down_proj = nn.Linear(hidden_dim, dim, bias=False)

    def forward(self, x):
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class MoE(nn.Module):
    def __init__(self, dim, moe_inter_dim, n_routed_experts=8, n_activated_experts=2, n_shared_experts=2):
        super().__init__()
        self.dim = dim
        self.n_routed_experts = n_routed_experts
        self.n_activated_experts = n_activated_experts
        self.gate = Gate(dim=dim, topk=n_activated_experts, n_routed_experts=n_routed_experts)
        self.experts = nn.ModuleList([MLP(dim, moe_inter_dim) for _ in range(self.n_routed_experts)])
        self.shared_experts = MLP(dim, n_shared_experts * moe_inter_dim)
        self.aux_loss = 0.0

    def forward(self, x):
        shape = x.size()
        x = x.view(-1, self.dim)
        weights, indices, aux_loss = self.gate(x)
        y = torch.zeros_like(x)
        counts = torch.bincount(indices.flatten(), minlength=self.n_routed_experts).tolist()
        for i in range(self.n_routed_experts):
            if counts[i] == 0:
                continue
            idx, top = torch.where(indices == i)
            y[idx] += self.experts[i](x[idx]) * weights[idx, top, None]
        z = self.shared_experts(x)
        self.aux_loss = aux_loss
        return (y + z).view(shape)


class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def _norm(self, x):
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)

    def forward(self, x):
        return self.weight * self._norm(x.float()).type_as(x)


def rotate_half(x):
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat((-x2, x1), dim=-1)


def precompute_freqs_cis(dim, end, rope_base):
    freqs = 1.0 / (rope_base ** (torch.arange(0, dim, 2).float() / dim))
    t = torch.arange(end)
    freqs = torch.outer(t, freqs).float()
    freqs_cos = torch.cat([torch.cos(freqs), torch.cos(freqs)], dim=-1)
    freqs_sin = torch.cat([torch.sin(freqs), torch.sin(freqs)], dim=-1)
    return freqs_cos, freqs_sin


def apply_rotary(x, cos, sin):
    cos = cos[None, None, :, :].to(device=x.device, dtype=x.dtype)
    sin = sin[None, None, :, :].to(device=x.device, dtype=x.dtype)
    return x * cos + rotate_half(x) * sin


def repeat_kv(x, n_rep):
    b, t, h, d = x.shape
    if n_rep == 1:
        return x
    return x[:, :, :, None, :].expand(b, t, h, n_rep, d).reshape(b, t, h * n_rep, d)


class Attention(nn.Module):
    def __init__(self, dim, head_dim=64, num_key_value_heads=2, qk_norm=True):
        super().__init__()
        if dim % head_dim != 0:
            raise ValueError("dim must be divisible by head_dim")
        self.head_dim = head_dim
        self.n_heads = dim // head_dim
        self.kv_heads = num_key_value_heads
        if self.n_heads % self.kv_heads != 0:
            raise ValueError("n_heads must be divisible by num_key_value_heads")
        self.n_rep = self.n_heads // self.kv_heads
        self.wq = nn.Linear(dim, self.n_heads * self.head_dim, bias=False)
        self.wk = nn.Linear(dim, self.kv_heads * self.head_dim, bias=False)
        self.wv = nn.Linear(dim, self.kv_heads * self.head_dim, bias=False)
        self.wo = nn.Linear(self.n_heads * self.head_dim, dim, bias=False)
        self.qk_norm = qk_norm
        if self.qk_norm:
            self.q_norm = RMSNorm(self.head_dim)
            self.k_norm = RMSNorm(self.head_dim)

    def forward(self, x, signal_token_num=0, cos=None, sin=None):
        b, seq_len, _ = x.shape
        mask = torch.tril(torch.ones(seq_len, seq_len, device=x.device)).bool()
        if signal_token_num > 0:
            mask[:signal_token_num, :signal_token_num] = 1

        xq = self.wq(x).view(b, seq_len, self.n_heads, self.head_dim)
        xk = self.wk(x).view(b, seq_len, self.kv_heads, self.head_dim)
        xv = self.wv(x).view(b, seq_len, self.kv_heads, self.head_dim)
        if self.qk_norm:
            xq = self.q_norm(xq)
            xk = self.k_norm(xk)

        xq = xq.transpose(1, 2)
        xk = repeat_kv(xk, self.n_rep).transpose(1, 2)
        xv = repeat_kv(xv, self.n_rep).transpose(1, 2)
        if cos is not None and sin is not None:
            xq = apply_rotary(xq, cos, sin)
            xk = apply_rotary(xk, cos, sin)

        output = F.scaled_dot_product_attention(
            xq, xk, xv,
            attn_mask=mask,
            is_causal=False
        )
        output = output.transpose(1, 2).reshape(b, seq_len, -1)
        output = self.wo(output)
        return output


class SignalEncoder(nn.Module):
    def __init__(self, dim=512, head_dim=64, num_key_value_heads=2):
        super().__init__()
        self.dim = dim
        self.n_fft = 200
        self.hop_length = self.n_fft // 4
        self.register_buffer("hann_window", torch.hann_window(self.n_fft))
        self.conv_proj = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1, stride=2),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1, stride=2),
            nn.ReLU(),
            nn.Conv2d(32, dim, kernel_size=(5, 1), stride=(5, 1), bias=False),
            nn.GroupNorm(num_groups=32, num_channels=dim),
            nn.GELU()
        )
        self.channel_norm = RMSNorm(dim)
        self.channel_attn = Attention(dim, head_dim=head_dim, num_key_value_heads=num_key_value_heads)

    def forward(self, x):
        b, c, l = x.shape
        x_mean = torch.mean(x, dim=-1, keepdim=True)
        x_std = torch.std(x, dim=-1, keepdim=True)
        x = (x - x_mean) / (x_std + 1e-6)
        remainder = 200 * math.ceil(l / 200) - l
        if remainder > 0:
            x = F.pad(x, (0, remainder), mode="constant", value=0)
        x = x.reshape(b * c, -1)
        x = torch.abs(torch.stft(
            x,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            window=self.hann_window,
            return_complex=True,
            normalized=True
        ))
        x = torch.log1p(x)
        x = x.unsqueeze(1)
        x = self.conv_proj(x)
        _, d, h, w = x.shape
        x = rearrange(x, "(b c) d h w -> (b h w) c d", b=b, c=c, d=d, h=h, w=w)
        x = x + self.channel_attn(self.channel_norm(x), signal_token_num=x.shape[1])
        x = torch.mean(x, dim=1, keepdim=True)
        x = rearrange(x, "(b h w) 1 d -> b (h w) d", b=b, d=d, h=h, w=w)
        return x


class TransformerBlock(nn.Module):
    def __init__(self, dim, hidden_dim, head_dim=64, num_key_value_heads=2, use_moe=False):
        super().__init__()
        self.self_attn = Attention(dim=dim, head_dim=head_dim, num_key_value_heads=num_key_value_heads)
        if use_moe:
            self.mlp = MoE(dim=dim, moe_inter_dim=dim)
        else:
            self.mlp = MLP(dim=dim, hidden_dim=hidden_dim)
        self.input_norm = RMSNorm(dim)
        self.post_attention_layernorm = RMSNorm(dim)

    def forward(self, x, signal_token_num=0, cos=None, sin=None):
        x = x + self.self_attn(self.input_norm(x), signal_token_num=signal_token_num, cos=cos, sin=sin)
        x = x + self.mlp(self.post_attention_layernorm(x))
        return x


class Metis(nn.Module):
    def __init__(self, config=MetisConfig()):
        super().__init__()
        self.config = config
        self.dim = config.dim
        self.n_layers = config.n_layers
        self.num_heads = config.dim // config.head_dim

        self.Encoder = SignalEncoder(
            dim=config.dim,
            head_dim=config.head_dim,
            num_key_value_heads=config.num_key_value_heads
        )
        self.embedding = nn.Embedding(config.vocab_size, config.dim)

        self.block = nn.ModuleList([
            TransformerBlock(
                dim=config.dim,
                hidden_dim=config.hidden_dim,
                head_dim=config.head_dim,
                num_key_value_heads=config.num_key_value_heads,
                use_moe=False
            ) if i < 2 else TransformerBlock(
                dim=config.dim,
                hidden_dim=config.hidden_dim,
                head_dim=config.head_dim,
                num_key_value_heads=config.num_key_value_heads,
                use_moe=True
            )
            for i in range(config.n_layers)
        ])

        self.norm = RMSNorm(config.dim)
        self.lm_head = nn.Linear(config.dim, config.vocab_size, bias=False)
        self.embedding.weight = self.lm_head.weight

        signal_cos, signal_sin = precompute_freqs_cis(
            config.head_dim,
            config.max_signal_seq_len,
            config.signal_rope_base
        )
        text_cos, text_sin = precompute_freqs_cis(
            config.head_dim,
            config.max_text_seq_len,
            config.text_rope_base
        )

        self.register_buffer("signal_cos", signal_cos, persistent=False)
        self.register_buffer("signal_sin", signal_sin, persistent=False)
        self.register_buffer("text_cos", text_cos, persistent=False)
        self.register_buffer("text_sin", text_sin, persistent=False)

    def get_rope(self, signal_len, text_len, device):
        cos = self.signal_cos[:signal_len]
        sin = self.signal_sin[:signal_len]

        if text_len > 0:
            cos = torch.cat([cos, self.text_cos[:text_len]], dim=0)
            sin = torch.cat([sin, self.text_sin[:text_len]], dim=0)

        return cos.to(device), sin.to(device)

    def forward(self, signal, input_ids=None, return_aux_loss=False):
        signal_embeds = self.Encoder(signal)
        signal_token_num = signal_embeds.shape[1]

        if input_ids is not None:
            language_embeds = self.embedding(input_ids)
            hidden_states = torch.cat([signal_embeds, language_embeds], dim=1)
            text_token_num = language_embeds.shape[1]
        else:
            hidden_states = signal_embeds
            text_token_num = 0

        cos, sin = self.get_rope(signal_token_num, text_token_num, hidden_states.device)

        for layer_idx, layer in enumerate(self.block):
            hidden_states = layer(hidden_states, signal_token_num=signal_token_num, cos=cos, sin=sin)

        hidden_states = self.norm(hidden_states)

        if input_ids is not None:
            hidden_states = self.lm_head(hidden_states[:, signal_token_num:])

        if return_aux_loss:
            aux_loss = sum(
                layer.mlp.aux_loss
                for layer in self.block
                if isinstance(layer.mlp, MoE)
            )
            return hidden_states, aux_loss

        return hidden_states


class MetisClassifier(nn.Module):
    def __init__(self, config=MetisConfig()):
        super().__init__()
        self.backbone = Metis(config)
        self.classification_head = nn.Linear(config.dim, config.num_classes)

    def forward(self, x):
        hidden_states = self.backbone(x)
        hidden_states = torch.mean(hidden_states, dim=1, keepdim=False)
        pre = self.classification_head(hidden_states)
        return pre

if __name__ == "__main__":
    config = MetisConfig()
    model = Metis(config)

    x = torch.randn(1, 10, 1000)
    ids = torch.randint(low=1, high=20000, size=(1, 20))

    y = model(x, ids)
    print(y.shape)