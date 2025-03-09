import os

#==============================================================================
# DEFAULT CONFIGURATION SETTINGS
#==============================================================================
# Default configuration values
DEFAULT_CONFIG = {
    "USE_S3": False,               # Whether to use S3 for video storage (vs local)
    "S3_BUCKET_NAME": "wound-care-videos",  # S3 bucket name if using S3
    "S3_PREFIX": "videos/",        # Prefix/folder for videos in S3 bucket
    "AWS_REGION": "us-east-1",     # AWS region for S3 bucket
    "DEBUG": False                 # Debug mode flag
}

#==============================================================================
# CONFIGURATION HANDLING
#==============================================================================
def get_config():
    """
    Get configuration from environment variables or use defaults
    """
    # Start with the default config
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables if they exist
    for key in config:
        env_value = os.environ.get(key)
        if env_value is not None:
            # Convert string to boolean for boolean values
            if isinstance(config[key], bool):
                config[key] = env_value.lower() == 'true'
            else:
                config[key] = env_value
    
    return config
