"""Configuration processing with defaults and validation."""

import json
from pathlib import Path
from typing import Dict, Any
import copy


def load_defaults() -> Dict[str, Any]:
    """Load default configuration from package."""
    defaults_path = Path(__file__).parent / "config_defaults.json"
    with open(defaults_path, 'r') as f:
        return json.load(f)


def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries, with override values taking precedence.
    
    Args:
        base: Base dictionary (defaults)
        override: Override dictionary (user config)
    
    Returns:
        Merged dictionary
    """
    result = copy.deepcopy(base)
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    
    return result


def _require(config: Dict[str, Any], path: str, message: str) -> None:
    parts = path.split('.')
    cur: Any = config
    for part in parts:
        if not isinstance(cur, dict) or part not in cur or cur[part] in (None, ""):
            raise ValueError(message)
        cur = cur[part]


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration has required fields for the selected simulator."""
    _require(config, "BASELINE", "Configuration must include BASELINE section")

    baseline = config["BASELINE"]
    _require({"BASELINE": baseline}, "BASELINE.DATE_START", "BASELINE.DATE_START is required")
    _require({"BASELINE": baseline}, "BASELINE.DATE_END", "BASELINE.DATE_END is required")

    _require(config, "OUTPUT.dir", "Configuration must include OUTPUT.dir")
    _require(config, "OUTPUT.file_prefix", "Configuration must include OUTPUT.file_prefix")

    simulator = config.get("SIMULATOR", {})
    mode = simulator.get("mode")
    if mode not in {"rule", "synthesizer"}:
        raise ValueError("SIMULATOR.mode must be 'rule' or 'synthesizer'")

    if mode == "rule":
        if "RULE" not in config:
            raise ValueError("RULE section is required when SIMULATOR.mode='rule'")
    if mode == "synthesizer":
        if "SYNTHESIZER" not in config:
            raise ValueError("SYNTHESIZER section is required when SIMULATOR.mode='synthesizer'")
        syn = config["SYNTHESIZER"]
        _require({"SYNTHESIZER": syn}, "SYNTHESIZER.SYNTHESIZER_TYPE", "SYNTHESIZER.SYNTHESIZER_TYPE is required")


def process_config(config_path: str) -> Dict[str, Any]:
    """
    Load, merge with defaults, and validate configuration.
    
    Args:
        config_path: Path to user configuration file
    
    Returns:
        Complete validated configuration
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load user config
    with open(config_file, 'r') as f:
        user_config = json.load(f)
    
    # Load defaults
    defaults = load_defaults()
    
    # Merge user config over defaults
    config = deep_merge(defaults, user_config)
    
    validate_config(config)
    return config
