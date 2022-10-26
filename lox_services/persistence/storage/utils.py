from lox_services.persistence.config import ENVIRONMENT

def use_environment_bucket(bucket_name: str):
    """Modifies the bucket_name if using development mode."""
    if not bucket_name:
        print("bucket_name:", type(bucket_name))
        raise ValueError("Bucket name must be provided.")
    
    if ENVIRONMENT == "development":
        bucket_name += "_development"
    
    return bucket_name

if __name__ == "__main__":
    print(use_environment_bucket("Hello"))
