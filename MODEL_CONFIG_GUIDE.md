# Model Configuration Guide

This guide explains how to configure model parameters in Vidur simulator using the YAML configuration file.

## Overview

Vidur now supports two ways to define model configurations:

1. **YAML Configuration File** (`model_configs.yaml`) - **Recommended for easy customization**
2. **Python Hardcoded Configs** (`vidur/config/model_config.py`) - Legacy method, used as fallback

## Using YAML Configuration

### Quick Start

1. The `model_configs.yaml` file is located in the project root directory
2. All model parameters are explicitly defined in this file
3. You can modify existing models or add new ones

### File Structure

```yaml
models:
  "model-name-here":
    num_layers: 32
    num_q_heads: 32
    num_kv_heads: 32
    embedding_dim: 4096
    mlp_hidden_dim: 11008
    max_position_embeddings: 4096
    use_gated_mlp: true
    use_bias: false
    use_qkv_bias: false
    activation: "silu"
    norm: "rms_norm"
    post_attn_norm: true
    vocab_size: 32768
    is_neox_style: true
    rope_theta: 10000.0
    rope_scaling: null
    partial_rotary_factor: 1.0
    no_tensor_parallel: false
```

### Parameter Descriptions

| Parameter | Type | Description | Common Values |
|-----------|------|-------------|---------------|
| `num_layers` | int | Number of transformer layers | 32, 48, 80 |
| `num_q_heads` | int | Number of query attention heads | 32, 64 |
| `num_kv_heads` | int | Number of key-value heads (GQA) | 8, 32, 64 |
| `embedding_dim` | int | Hidden dimension size | 4096, 8192 |
| `mlp_hidden_dim` | int | MLP intermediate dimension | 11008, 28672 |
| `max_position_embeddings` | int | Maximum sequence length | 4096, 8192, 32768 |
| `use_gated_mlp` | bool | Use gated MLP (SwiGLU) | true/false |
| `use_bias` | bool | Use bias in linear layers | true/false |
| `use_qkv_bias` | bool | Use bias in attention QKV | true/false |
| `activation` | string | Activation function | "silu", "gelu" |
| `norm` | string | Normalization type | "rms_norm", "layer_norm" |
| `post_attn_norm` | bool | Normalization after attention | true/false |
| `vocab_size` | int | Vocabulary size | 32768, 128256 |
| `is_neox_style` | bool | Use GPT-NeoX style architecture | true/false |
| `rope_theta` | float | RoPE base frequency | 10000.0, 500000.0 |
| `rope_scaling` | dict/null | RoPE scaling configuration | null or dict |
| `partial_rotary_factor` | float | Fraction of dim for RoPE | 1.0 (full), 0.4 (partial) |
| `no_tensor_parallel` | bool | Disable tensor parallelism | true/false |

### Adding a New Model

To add a new model, simply add an entry to the `models` section in `model_configs.yaml`:

```yaml
models:
  # ... existing models ...
  
  "my-org/my-custom-model-7b":
    num_layers: 32
    num_q_heads: 32
    num_kv_heads: 32
    embedding_dim: 4096
    mlp_hidden_dim: 11008
    max_position_embeddings: 4096
    use_gated_mlp: true
    use_bias: false
    use_qkv_bias: false
    activation: "silu"
    norm: "rms_norm"
    post_attn_norm: true
    vocab_size: 32000
    is_neox_style: true
    rope_theta: 10000.0
    rope_scaling: null
    partial_rotary_factor: 1.0
    no_tensor_parallel: false
```

Then use it in your simulation:

```bash
python run.py prefill my-org/my-custom-model-7b A100 --batch_size 4 --sequence_length 256
```

Or with the full simulator:

```bash
python -m vidur.main --replica_config_model_name "my-org/my-custom-model-7b" --replica_config_device a100
```

### Modifying Existing Models

To modify an existing model's parameters (e.g., to experiment with different configurations):

1. Open `model_configs.yaml`
2. Find the model you want to modify
3. Change the parameters you want to test
4. Save the file
5. Run your simulation

Example: Increasing Llama-2-7B's context length:

```yaml
"meta-llama/Llama-2-7b-hf":
  # ... other parameters ...
  max_position_embeddings: 8192  # Changed from 4096 to 8192
  # ... rest of parameters ...
```

### Configuration Priority

The simulator uses the following priority order:

1. **YAML Configuration** (highest priority)
   - Checked first when loading a model
   - Located at: `model_configs.yaml`

2. **Python Hardcoded Configuration** (fallback)
   - Used if model not found in YAML
   - Located at: `vidur/config/model_config.py`

3. **Error** (if not found in either)
   - Simulator will raise an error with a helpful message

### Environment Variable

You can also specify a custom location for the YAML config file:

```bash
export VIDUR_CONFIG_DIR=/path/to/config/directory
python run.py prefill llama-7b A100 --batch_size 4 --sequence_length 256
```

The simulator will look for `model_configs.yaml` in:
1. Project root directory (default)
2. Current working directory
3. Directory specified by `VIDUR_CONFIG_DIR` environment variable

## Examples

### Example 1: Adding a Llama-3-405B Model

```yaml
"meta-llama/Meta-Llama-3-405B":
  num_layers: 126
  num_q_heads: 128
  num_kv_heads: 8
  embedding_dim: 16384
  mlp_hidden_dim: 53248
  max_position_embeddings: 8192
  use_gated_mlp: true
  use_bias: false
  use_qkv_bias: false
  activation: "silu"
  norm: "rms_norm"
  post_attn_norm: true
  vocab_size: 128256
  is_neox_style: true
  rope_theta: 500000.0
  rope_scaling: null
  partial_rotary_factor: 1.0
  no_tensor_parallel: false
```

### Example 2: Adding a Mistral-7B Model

```yaml
"mistralai/Mistral-7B-v0.1":
  num_layers: 32
  num_q_heads: 32
  num_kv_heads: 8  # Grouped Query Attention
  embedding_dim: 4096
  mlp_hidden_dim: 14336
  max_position_embeddings: 32768  # Sliding window attention
  use_gated_mlp: true
  use_bias: false
  use_qkv_bias: false
  activation: "silu"
  norm: "rms_norm"
  post_attn_norm: true
  vocab_size: 32000
  is_neox_style: true
  rope_theta: 10000.0
  rope_scaling: null
  partial_rotary_factor: 1.0
  no_tensor_parallel: false
```

### Example 3: Experimenting with Architectural Changes

```yaml
"llama-2-7b-experimental":
  num_layers: 32
  num_q_heads: 32
  num_kv_heads: 4  # Reduced from 32 to test more aggressive GQA
  embedding_dim: 4096
  mlp_hidden_dim: 11008
  max_position_embeddings: 16384  # Extended context
  use_gated_mlp: true
  use_bias: false
  use_qkv_bias: false
  activation: "silu"
  norm: "rms_norm"
  post_attn_norm: true
  vocab_size: 32768
  is_neox_style: true
  rope_theta: 100000.0  # Increased for longer context
  rope_scaling: null
  partial_rotary_factor: 1.0
  no_tensor_parallel: false
```

## Tips and Best Practices

1. **Keep a Backup**: Before modifying `model_configs.yaml`, keep a backup copy
2. **Model Naming**: Use descriptive names like `"org/model-size-variant"`
3. **Comments**: Add comments in YAML to document your changes
4. **Validation**: The simulator will validate parameters and show errors if something is wrong
5. **Logging**: Check simulator logs to confirm which configuration source is being used

## Troubleshooting

### Model Not Found Error

```
ValueError: [BaseModelConfig] Invalid model name: my-model. Add it to model_configs.yaml or as a Python subclass.
```

**Solution**: Add your model configuration to `model_configs.yaml`

### YAML Parsing Error

```
Error loading model_configs.yaml: ... Using hardcoded configs only.
```

**Solution**: Check your YAML syntax (indentation, quotes, colons)

### Wrong Configuration Being Used

Check the simulator logs for messages like:
- `"Using YAML configuration for model: ..."` - Good! Using YAML
- `"Using hardcoded configuration for model: ..."` - Falling back to Python

## Additional Resources

- [Original Model Config Python File](vidur/config/model_config.py)
- [YAML Syntax Guide](https://yaml.org/spec/1.2.2/)
- [Vidur Documentation](README.md)

## Support

If you encounter issues with model configuration, please check:
1. YAML file syntax and indentation
2. All required parameters are present
3. Parameter types match the expected types
4. Simulator log messages for hints

For more help, see the main [README](README.md) or open an issue on GitHub.

