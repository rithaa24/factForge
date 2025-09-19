"""
Configuration for embedding models
"""
from typing import Dict, Any, List
import os

# Model configurations
EMBEDDING_MODELS = {
    "paraphrase-multilingual-mpnet-base-v2": {
        "name": "paraphrase-multilingual-mpnet-base-v2",
        "dimension": 768,
        "max_length": 512,
        "languages": ["en", "hi", "ta", "kn", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko"],
        "description": "Multilingual sentence transformer model"
    },
    "all-MiniLM-L6-v2": {
        "name": "all-MiniLM-L6-v2", 
        "dimension": 384,
        "max_length": 256,
        "languages": ["en"],
        "description": "Lightweight English sentence transformer"
    },
    "distiluse-base-multilingual-cased": {
        "name": "distiluse-base-multilingual-cased",
        "dimension": 512,
        "max_length": 512,
        "languages": ["en", "hi", "ta", "kn", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko"],
        "description": "Multilingual Universal Sentence Encoder"
    }
}

# Default model
DEFAULT_MODEL = "paraphrase-multilingual-mpnet-base-v2"

# Language-specific configurations
LANGUAGE_CONFIGS = {
    "en": {
        "normalize": True,
        "lowercase": True,
        "remove_punctuation": False,
        "max_length": 512
    },
    "hi": {
        "normalize": True,
        "lowercase": False,
        "remove_punctuation": False,
        "max_length": 512,
        "unicode_normalization": "NFC"
    },
    "ta": {
        "normalize": True,
        "lowercase": False,
        "remove_punctuation": False,
        "max_length": 512,
        "unicode_normalization": "NFC"
    },
    "kn": {
        "normalize": True,
        "lowercase": False,
        "remove_punctuation": False,
        "max_length": 512,
        "unicode_normalization": "NFC"
    }
}

# Model selection based on environment
def get_model_config() -> Dict[str, Any]:
    """Get model configuration based on environment variables"""
    model_name = os.getenv("EMBEDDING_MODEL", DEFAULT_MODEL)
    
    if model_name not in EMBEDDING_MODELS:
        print(f"Warning: Model {model_name} not found, using default {DEFAULT_MODEL}")
        model_name = DEFAULT_MODEL
    
    return EMBEDDING_MODELS[model_name]

# Language detection thresholds
LANGUAGE_THRESHOLDS = {
    "en": 0.7,
    "hi": 0.6,
    "ta": 0.6,
    "kn": 0.6
}

# Similarity thresholds for retrieval
SIMILARITY_THRESHOLDS = {
    "en": 0.7,
    "hi": 0.6,
    "ta": 0.6,
    "kn": 0.6
}

# Batch processing configuration
BATCH_CONFIG = {
    "batch_size": 32,
    "max_workers": 4,
    "timeout": 30
}

# Cache configuration
CACHE_CONFIG = {
    "enabled": True,
    "ttl": 3600,  # 1 hour
    "max_size": 10000
}

# Supported languages
SUPPORTED_LANGUAGES = ["en", "hi", "ta", "kn"]

# Model download configuration
DOWNLOAD_CONFIG = {
    "cache_dir": os.path.join(os.path.dirname(__file__), "models"),
    "use_auth_token": False,
    "force_download": False
}

def get_language_config(language: str) -> Dict[str, Any]:
    """Get language-specific configuration"""
    return LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["en"])

def is_language_supported(language: str) -> bool:
    """Check if language is supported"""
    return language in SUPPORTED_LANGUAGES

def get_similarity_threshold(language: str) -> float:
    """Get similarity threshold for a language"""
    return SIMILARITY_THRESHOLDS.get(language, 0.7)

def get_language_threshold(language: str) -> float:
    """Get language detection threshold"""
    return LANGUAGE_THRESHOLDS.get(language, 0.7)
