"""
Utility functions and helper classes for the Optimizer system.

This module provides common utilities used across different components
of the Optimizer application.
"""

import os
import json
import time
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import re


class Logger:
    """Simple logging utility for the Optimizer system."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


class ConfigManager:
    """Configuration manager for the Optimizer system."""
    
    def __init__(self, config_file: str = ".env"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from environment and .env file."""
        # Load from .env file if it exists
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = value.strip().strip('"\'')
        
        # Override with environment variables
        self.config.update(os.environ)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def get_required(self, key: str) -> str:
        """Get required configuration value, raise error if missing."""
        value = self.config.get(key)
        if value is None:
            raise ValueError(f"Required configuration key '{key}' is missing")
        return value
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get all Gemini API keys."""
        keys = {}
        for i in range(1, 6):  # GEMINI_API_KEY_1 through GEMINI_API_KEY_5
            key_name = f"GEMINI_API_KEY_{i}"
            key_value = self.get(key_name)
            if key_value:
                keys[key_name] = key_value
        
        serpapi_key = self.get("SERPAPI_KEY")
        if serpapi_key:
            keys["SERPAPI_KEY"] = serpapi_key
        
        return keys


class TextProcessor:
    """Text processing utilities."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?;:()\'"]+', '', text)
        
        return text
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 2000, suffix: str = "...") -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text (simple implementation)."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stop words and count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    @staticmethod
    def format_markdown(text: str) -> str:
        """Basic markdown formatting."""
        if not text:
            return ""
        
        # Convert headers
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        # Convert bold and italic
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        
        # Convert line breaks
        text = text.replace('\n', '<br>')
        
        return text


class FileUtils:
    """File and path utilities."""
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists, create if it doesn't."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logging.error(f"Failed to create directory {path}: {e}")
            return False
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Convert filename to safe format."""
        # Remove or replace unsafe characters
        safe_name = re.sub(r'[^\w\-_.]', '_', filename)
        # Limit length
        if len(safe_name) > 255:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[:255-len(ext)] + ext
        return safe_name
    
    @staticmethod
    def get_file_hash(filepath: str) -> Optional[str]:
        """Get MD5 hash of file."""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logging.error(f"Failed to hash file {filepath}: {e}")
            return None
    
    @staticmethod
    def get_file_info(filepath: str) -> Dict[str, Any]:
        """Get comprehensive file information."""
        try:
            path = Path(filepath)
            stat = path.stat()
            
            return {
                "name": path.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "extension": path.suffix,
                "exists": path.exists(),
                "is_file": path.is_file(),
                "hash": FileUtils.get_file_hash(filepath) if path.exists() else None
            }
        except Exception as e:
            logging.error(f"Failed to get file info for {filepath}: {e}")
            return {"exists": False, "error": str(e)}


class DataValidator:
    """Data validation utilities."""
    
    @staticmethod
    def validate_project_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate project data structure."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['project_data']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Project data content validation
        project_text = data.get('project_data', '')
        if len(project_text.strip()) < 100:
            warnings.append("Project description is quite short - more detail would improve analysis")
        
        if len(project_text) > 50000:
            warnings.append("Project description is very long - consider summarizing key points")
        
        # Team info validation
        team_info = data.get('team_info', '')
        if not team_info and len(project_text) > 1000:
            warnings.append("Team information not provided - this could help with analysis")
        
        # Files validation
        files = data.get('files', [])
        if len(files) > 10:
            warnings.append("Many files uploaded - processing might take longer")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_api_keys(keys: Dict[str, str]) -> Dict[str, Any]:
        """Validate API keys structure."""
        errors = []
        warnings = []
        
        # Check required Gemini keys
        required_gemini_keys = [f"GEMINI_API_KEY_{i}" for i in range(1, 6)]
        for key in required_gemini_keys:
            if not keys.get(key):
                errors.append(f"Missing API key: {key}")
            elif len(keys[key]) < 20:
                warnings.append(f"API key {key} seems too short")
        
        # Check SerpAPI key
        if not keys.get("SERPAPI_KEY"):
            errors.append("Missing SERPAPI_KEY")
        elif len(keys["SERPAPI_KEY"]) < 20:
            warnings.append("SERPAPI_KEY seems too short")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "keys_count": len([k for k in keys.values() if k])
        }


class PerformanceTimer:
    """Simple performance timing utility."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"⏱️ {self.name} completed in {duration:.2f} seconds")
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time


class ResponseFormatter:
    """Utilities for formatting API responses."""
    
    @staticmethod
    def success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
        """Create successful API response."""
        return {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def error_response(error: str, code: int = 500, details: Any = None) -> Dict[str, Any]:
        """Create error API response."""
        response = {
            "status": "error",
            "error": error,
            "code": code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if details:
            response["details"] = details
        
        return response
    
    @staticmethod
    def format_agent_result(result: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """Format agent result for consistent API response."""
        formatted = {
            "agent": agent_name,
            "status": result.get("status", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add data based on status
        if result.get("status") == "success":
            # Remove status from data to avoid duplication
            data = {k: v for k, v in result.items() if k != "status"}
            formatted["data"] = data
        else:
            formatted["error"] = result.get("error", "Unknown error")
        
        return formatted


# Convenience functions
def get_logger(name: str) -> Logger:
    """Get logger instance."""
    return Logger(name)


def load_config(config_file: str = ".env") -> ConfigManager:
    """Load configuration."""
    return ConfigManager(config_file)


def time_operation(name: str):
    """Decorator for timing operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceTimer(name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage and testing
if __name__ == "__main__":
    # Test configuration manager
    config = load_config()
    print("🔧 Configuration loaded")
    
    # Test text processing
    processor = TextProcessor()
    sample_text = "This is a **sample** text with *formatting* and keywords about startup business model."
    
    keywords = processor.extract_keywords(sample_text)
    print(f"📝 Keywords: {keywords}")
    
    cleaned = processor.clean_text(sample_text)
    print(f"🧹 Cleaned text: {cleaned}")
    
    # Test validation
    validator = DataValidator()
    test_data = {
        "project_data": "A mobile app for restaurants",
        "team_info": "Small technical team"
    }
    
    validation = validator.validate_project_data(test_data)
    print(f"✅ Validation result: {validation}")
    
    # Test performance timer
    with PerformanceTimer("Sample operation"):
        time.sleep(0.1)  # Simulate work
    
    print("🎯 Utils module test completed")