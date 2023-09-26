try:
  import torch
except ImportError:
  print("pytorch is not installed.")
  exit()

from torch import Tensor
from typing import Optional
from pathlib import Path
from ._version import __version__

try:
  from warp_attention.warp_attention_torch_cpp import create_module

  _proj_dir = Path(__file__).resolve().parent
  _kernel_dir = _proj_dir / "kernel"

  _kernel_map = {
    "8.0": f"{_kernel_dir}/warp_attn_forward_sm80.cubin",
    "8.6": f"{_kernel_dir}/warp_attn_forward_sm86.cubin",
  }
  _kernel_config = torch.load(_kernel_dir / "kernel_config.pt")
  _kernel_module = create_module(_kernel_config, _kernel_map)
  max_kernel_version = _kernel_config.shape[3] - 1
  max_gear = _kernel_config.shape[2] - 1

  def _warp_attention_forward(
      query: Tensor,
      key: Tensor,
      value: Tensor,
      scale: Optional[float] = None,
      out: Optional[Tensor] = None,
      version: int = 0,
      gear: int = 4,
      is_causal: bool = False,
    ):
    if out is None:
      out = torch.zeros_like(query)
    if scale is None:
      scale = query.shape[-1] ** (-0.5)

    assert 0 <= version <= max_kernel_version, f"version should be between 0 and {max_kernel_version}, including 0 and {max_kernel_version}"
    assert 0 <= gear <= max_kernel_version, f"gear should be between 0 and {max_gear}, including 0 and {max_gear}"

    stream = torch.cuda.current_stream()

    _kernel_module.run(
      query, key, value, out, 
      scale, gear, version, is_causal, stream.cuda_stream
    )
    return out

except ImportError:
  print("warp_attention is installed incorrectly.")