import json
import logging
import sys
from datetime import datetime

class CloudLoggingFormatter(logging.Formatter):
    """
    Standardizes logs to the Google Cloud Structured Logging format.
    https://cloud.google.com/logging/docs/structured-logging
    """
    def format(self, record):
        log_entry = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "logging.googleapis.com/sourceLocation": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName
            },
            "logger": record.name,
            "module": record.module
        }
        
        # Merge extra fields if present
        if hasattr(record, "extra_info"):
            log_entry.update(record.extra_info)
            
        return json.dumps(log_entry)

def setup_cloud_logging():
    """Configure the root logger for GCP Cloud Logging."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(CloudLoggingFormatter())
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Disable default handlers to avoid duplicate logs
    for h in root_logger.handlers[:-1]:
        root_logger.removeHandler(h)
