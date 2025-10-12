from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import yaml
import os
from pathlib import Path

from vidur.config.base_fixed_config import BaseFixedConfig
from vidur.logger import init_logger
from vidur.types import ActivationType, NormType

logger = init_logger(__name__)

# Global variable to cache loaded YAML configs
_YAML_MODEL_CONFIGS = None


def load_yaml_model_configs():
    """Load model configurations from YAML file"""
    global _YAML_MODEL_CONFIGS
    
    if _YAML_MODEL_CONFIGS is not None:
        return _YAML_MODEL_CONFIGS
    
    # Try to find model_configs.yaml in the project root
    possible_paths = [
        Path(__file__).parent.parent.parent / "model_configs.yaml",  # From vidur/config
        Path.cwd() / "model_configs.yaml",  # Current working directory
        Path(os.environ.get("VIDUR_CONFIG_DIR", ".")) / "model_configs.yaml",  # Environment variable
    ]
    
    yaml_config_path = None
    for path in possible_paths:
        if path.exists():
            yaml_config_path = path
            break
    
    if yaml_config_path is None:
        logger.warning(f"model_configs.yaml not found in any of: {possible_paths}. Using hardcoded configs only.")
        _YAML_MODEL_CONFIGS = {}
        return _YAML_MODEL_CONFIGS
    
    try:
        with open(yaml_config_path, 'r') as f:
            data = yaml.safe_load(f)
            _YAML_MODEL_CONFIGS = data.get('models', {})
            logger.info(f"Loaded {len(_YAML_MODEL_CONFIGS)} model configurations from {yaml_config_path}")
            return _YAML_MODEL_CONFIGS
    except Exception as e:
        logger.error(f"Error loading model_configs.yaml: {e}. Using hardcoded configs only.")
        _YAML_MODEL_CONFIGS = {}
        return _YAML_MODEL_CONFIGS


def str_to_activation_type(activation_str: str) -> ActivationType:
    """Convert string to ActivationType enum"""
    mapping = {
        "silu": ActivationType.SILU,
        "gelu": ActivationType.GELU,
    }
    result = mapping.get(activation_str.lower())
    if result is None:
        logger.warning(f"Unknown activation type '{activation_str}', defaulting to SILU")
        return ActivationType.SILU
    return result


def str_to_norm_type(norm_str: str) -> NormType:
    """Convert string to NormType enum"""
    mapping = {
        "rms_norm": NormType.RMS_NORM,
        "layer_norm": NormType.LAYER_NORM,
    }
    return mapping.get(norm_str.lower(), NormType.RMS_NORM)


@dataclass
class BaseModelConfig(BaseFixedConfig):
    num_layers: int
    num_q_heads: int
    num_kv_heads: int
    embedding_dim: int
    mlp_hidden_dim: int
    max_position_embeddings: int
    use_gated_mlp: bool
    use_bias: bool
    use_qkv_bias: bool
    activation: ActivationType
    norm: NormType
    post_attn_norm: bool
    vocab_size: int
    is_neox_style: Optional[bool] = True
    rope_theta: Optional[float] = None
    rope_scaling: Optional[Dict[str, Any]] = None
    partial_rotary_factor: float = 1.0
    no_tensor_parallel: bool = False
    _model_name: Optional[str] = field(default=None, init=False, repr=False)
    
    def get_name(self) -> str:
        """Return the model name. For YAML configs, this is set during creation."""
        if self._model_name is not None:
            return self._model_name
        # Fall back to class method for hardcoded configs
        if hasattr(self.__class__, 'get_name') and callable(getattr(self.__class__, 'get_name')):
            return self.__class__.get_name()
        return "unknown-model"
    
    @classmethod
    def create_from_yaml(cls, model_name: str, yaml_config: Dict[str, Any]) -> "BaseModelConfig":
        """Create a BaseModelConfig instance from YAML configuration"""
        # Convert string enums to actual enum types
        config_dict = yaml_config.copy()
        
        if 'activation' in config_dict and isinstance(config_dict['activation'], str):
            config_dict['activation'] = str_to_activation_type(config_dict['activation'])
        
        if 'norm' in config_dict and isinstance(config_dict['norm'], str):
            config_dict['norm'] = str_to_norm_type(config_dict['norm'])
        
        logger.info(f"Creating model config for '{model_name}' from YAML")
        instance = cls(**config_dict)
        # Set the model name for this instance
        instance._model_name = model_name
        return instance
    
    @classmethod
    def create_from_name(cls, name: str) -> "BaseModelConfig":
        """
        Create a model config from name.
        First checks YAML config file, then falls back to hardcoded subclasses.
        """
        # Try loading from YAML first
        yaml_configs = load_yaml_model_configs()
        if name in yaml_configs:
            logger.info(f"Using YAML configuration for model: {name}")
            return cls.create_from_yaml(name, yaml_configs[name])
        
        # Fall back to hardcoded configs
        logger.info(f"Using hardcoded configuration for model: {name}")
        from vidur.config.utils import get_all_subclasses
        for subclass in get_all_subclasses(cls):
            if hasattr(subclass, 'get_name') and subclass.get_name() == name:
                return subclass()
        
        raise ValueError(f"[{cls.__name__}] Invalid model name: {name}. "
                        f"Add it to model_configs.yaml or as a Python subclass.")


@dataclass
class Llama2ModelConfig(BaseModelConfig):
    max_position_embeddings: int = 16384
    use_gated_mlp: bool = True
    use_bias: bool = False
    use_qkv_bias: bool = False
    activation: ActivationType = ActivationType.SILU
    norm: NormType = NormType.RMS_NORM
    post_attn_norm: bool = True
    vocab_size: int = 32768
    is_neox_style: Optional[bool] = True
    rope_theta: Optional[float] = 10000
    rope_scaling: Optional[Dict[str, Any]] = None
    partial_rotary_factor: float = 1.0
    no_tensor_parallel: bool = False

    @staticmethod
    def get_name():
        return "meta-llama/Llama-2-Config"


@dataclass
class CodeLlama34BModelConfig(Llama2ModelConfig):
    num_layers: int = 48
    num_q_heads: int = 64
    num_kv_heads: int = 8
    embedding_dim: int = 8192
    mlp_hidden_dim: int = 22016
    rope_theta: Optional[float] = 1000000

    @staticmethod
    def get_name():
        return "codellama/CodeLlama-34b-Instruct-hf"


@dataclass
class Llama2_7BModelConfig(Llama2ModelConfig):
    num_layers: int = 32
    num_q_heads: int = 32
    num_kv_heads: int = 32
    embedding_dim: int = 4096
    mlp_hidden_dim: int = 11008
    max_position_embeddings: int = 4096

    @staticmethod
    def get_name():
        return "meta-llama/Llama-2-7b-hf"


@dataclass
class Llama2_70BModelConfig(Llama2ModelConfig):
    num_layers: int = 80
    num_q_heads: int = 64
    num_kv_heads: int = 8
    embedding_dim: int = 8192
    mlp_hidden_dim: int = 28672
    max_position_embeddings: int = 4096

    @staticmethod
    def get_name():
        return "meta-llama/Llama-2-70b-hf"


@dataclass
class Llama3_8BModelConfig(Llama2ModelConfig):
    num_layers: int = 32
    num_q_heads: int = 32
    num_kv_heads: int = 8
    embedding_dim: int = 4096
    mlp_hidden_dim: int = 14336
    max_position_embeddings: int = 4096
    rope_theta: Optional[float] = 500000
    vocab_size: int = 128256

    @staticmethod
    def get_name():
        return "meta-llama/Meta-Llama-3-8B"


@dataclass
class Llama3_70BModelConfig(Llama2ModelConfig):
    num_layers: int = 80
    num_q_heads: int = 64
    num_kv_heads: int = 8
    embedding_dim: int = 8192
    mlp_hidden_dim: int = 28672
    max_position_embeddings: int = 8192
    rope_theta: Optional[float] = 500000
    vocab_size: int = 128256

    @staticmethod
    def get_name():
        return "meta-llama/Meta-Llama-3-70B"


@dataclass
class InternLMModelConfig(Llama2ModelConfig):
    max_position_embeddings: int = 4096
    vocab_size: int = 103168


@dataclass
class InternLM_20BModelConfig(InternLMModelConfig):
    num_layers: int = 60
    num_q_heads: int = 40
    num_kv_heads: int = 40
    embedding_dim: int = 5120
    mlp_hidden_dim: int = 13824

    @staticmethod
    def get_name():
        return "internlm/internlm-20b"


@dataclass
class InternLM2ModelConfig(Llama2ModelConfig):
    max_position_embeddings: int = 32768
    vocab_size: int = 92544


@dataclass
class InternLM2_20BModelConfig(InternLM2ModelConfig):
    num_layers: int = 48
    num_q_heads: int = 48
    num_kv_heads: int = 8
    embedding_dim: int = 6144
    mlp_hidden_dim: int = 16384
    rope_theta: Optional[float] = 1000000

    @staticmethod
    def get_name():
        return "internlm/internlm2-20b"


@dataclass
class Phi2ModelConfig(Llama2ModelConfig):
    num_layers: int = 32
    num_q_heads: int = 32
    num_kv_heads: int = 32
    embedding_dim: int = 2560
    mlp_hidden_dim: int = 10240
    max_position_embeddings: int = 2048
    use_gated_mlp: bool = False
    use_bias: bool = True
    use_qkv_bias: bool = True
    activation: ActivationType = ActivationType.GELU
    norm: NormType = NormType.LAYER_NORM
    post_attn_norm: bool = False
    vocab_size: int = 51200
    rope_scaling: Optional[Dict[str, Any]] = None
    rope_theta: Optional[float] = 10000
    partial_rotary_factor: float = 0.4
    no_tensor_parallel: bool = True

    @staticmethod
    def get_name():
        return "microsoft/phi-2"


@dataclass
class QwenModelConfig(Llama2ModelConfig):
    use_qkv_bias: bool = True
    max_position_embeddings: int = 32768
    vocab_size: int = 152064

    @staticmethod
    def get_name():
        return "Qwen/Qwen-Config"


@dataclass
class Qwen72BModelConfig(QwenModelConfig):
    num_layers: int = 80
    num_q_heads: int = 64
    num_kv_heads: int = 64
    embedding_dim: int = 8192
    mlp_hidden_dim: int = 24576
    rope_theta: Optional[float] = 1000000

    @staticmethod
    def get_name():
        return "Qwen/Qwen-72B"
