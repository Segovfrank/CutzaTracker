import os
from dotenv import load_dotenv

from odc import stac

def configure() -> None:
    endpoint, access_key, secret_key = _get_credentials()
    stac.configure_rio(
        cloud_defaults=True,
        verbose=False,
        aws={
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint
        },
        AWS_S3_ENDPOINT=endpoint,
        AWS_VIRTUAL_HOSTING=False,
        AWS_HTTPS="YES",
        GDAL_NUM_THREADS="1"
    )

def _get_credentials() -> tuple[str, str, str]:
    load_dotenv()
    try:
        return (
            os.getenv("ENDPOINT", "Undefined"),
            os.getenv("ACCESS_KEY", "Undefined"),
            os.getenv("SECRET_KEY", "Undefined")
        )
    except Exception as e:
        raise RuntimeError(f"No env file. Please set up your env and keys. {e}")