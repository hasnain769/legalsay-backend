import sys
import os
import json
from loguru import logger

def serialize_for_gcp(message):
    """
    Custom sink to transform Loguru records into Google Cloud Structured Logging format.
    """
    record = message.record
    
    # Map Loguru levels to GCP Severity
    severity_map = {
        "TRACE": "DEBUG", "DEBUG": "DEBUG", "INFO": "INFO", 
        "SUCCESS": "INFO", "WARNING": "WARNING", "ERROR": "ERROR", "CRITICAL": "CRITICAL"
    }
    
    log_entry = {
        "severity": severity_map.get(record["level"].name, "INFO"),
        "message": record["message"],
        "timestamp": record["time"].timestamp(),
        "logging.googleapis.com/sourceLocation": {
            "file": record["file"].name,
            "line": record["line"],
            "function": record["function"],
        }
    }

    # Trace ID linking for Google Cloud
    if "trace_id" in record["extra"]:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
        log_entry["logging.googleapis.com/trace"] = f"projects/{project_id}/traces/{record['extra']['trace_id']}"

    # Print JSON to stdout (Cloud Run captures this automatically)
    print(json.dumps(log_entry), file=sys.stdout)

def setup_logging():
    logger.remove() # Remove default handlers

    # Detect Environment: K_SERVICE is set automatically by Google Cloud Run
    is_production = bool(os.getenv("K_SERVICE")) or os.getenv("ENV") == "PRODUCTION"

    if is_production:
        # --- PRODUCTION MODE ---
        # Structured JSON for Cloud Logging
        logger.add(serialize_for_gcp, level="INFO")
    else:
        # --- DEVELOPMENT MODE ---
        # Sink 1: Pretty Console (Visual)
        logger.add(
            sys.stderr, 
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> - <level>{message}</level>", 
            level="DEBUG", 
            colorize=True
        )
        # Sink 2: JSON File (For LNAV Dashboard)
        logger.add(
            "server.log", 
            rotation="100 MB", 
            retention="2 days", 
            level="DEBUG", 
            serialize=True, 
            enqueue=True
        )

    return logger

logging = setup_logging()
