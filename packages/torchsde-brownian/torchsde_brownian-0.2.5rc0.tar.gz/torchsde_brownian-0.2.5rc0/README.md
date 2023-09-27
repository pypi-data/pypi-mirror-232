# torchsde_brownian

This library provides the Brownian motion generation code from [torchsde] version 0.2.5
as a standalone package `torchsde_brownian`.

It is mainly meant for use in downstream packages such as `k-diffusion` and `diffusers`,
for where it is a drop-in replacement: the dependency just needs to be changed,
and the import for `torchsde` to `torchsde_brownian`.

According to the authors of `torchsde`, that package is currently in maintenance mode,
so no further development, aside from possible compatibility fixes, is expected.

All credit for the original implementation goes to the authors of [torchsde],
Xuechen Li and Patrick Kidger.

The commit history of this repository has been kept intact so as to preserve
the provenance of the code and their contributions.

## Installation

```shell script
pip install torchsde_brownian
```

**Requirements:** Python >=3.8 and PyTorch >=1.6.0.

## Documentation

Available [here](./DOCUMENTATION.md).

## Citation and references

Please find citations and references in [torchsde]'s readme.

[torchsde]: https://github.com/google-research/torchsde
