
import os
import logging
import shutil
from pathlib import Path

import boto3
import snowflake.connector
from botocore.config import Config


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

# MinIO endpoint: inside Docker use the service name, outside Docker use localhost.
# The compose file publishes host port 9002 -> container port 9000.
if os.getenv("MINIO_ENDPOINT"):
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
elif os.path.exists("/.dockerenv"):
    MINIO_ENDPOINT = "http://minio:9000"
else:
    MINIO_ENDPOINT = "http://localhost:9002"

MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password123")
BUCKET = os.getenv("MINIO_BUCKET", "zomato-bronze-transaction")


def pick_download_dir():
    """Choose a writable directory with enough free space for downloads."""
    env_dir = os.getenv("LOCAL_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    candidate_roots = []
    if os.name == "nt":
        candidate_roots = [Path(f"{d}:\\") for d in "DEFGHIJKLMNOPQRSTUVWX" if Path(f"{d}:\\").exists()]
        if not candidate_roots:
            candidate_roots = [Path("C:\\")]
    else:
        candidate_roots = [
            Path("/opt/airflow/tmp"),
            Path("/tmp"),
            Path.home(),
        ]

    selected_dir = None
    selected_free = -1

    for root in candidate_roots:
        try:
            free_bytes = shutil.disk_usage(str(root.anchor if root.anchor else root)).free
        except OSError:
            continue

        candidate = root / "minio_downloads"
        if free_bytes > selected_free:
            selected_dir = candidate
            selected_free = free_bytes

    if selected_dir is None:
        selected_dir = Path("/tmp/minio_downloads") if os.name != "nt" else Path("C:/temp/minio_downloads")

    return selected_dir.resolve()


def ensure_free_space(path: Path, required_mb: int = 512):
    """Raise a clear error before the disk is exhausted."""
    root = str(path.anchor if path.anchor else path)
    free_bytes = shutil.disk_usage(root).free
    required_bytes = required_mb * 1024 * 1024

    if free_bytes < required_bytes:
        raise OSError(
            f"Not enough free space on {root}. "
            f"Available: {free_bytes / (1024**2):.1f} MB; required: {required_mb} MB"
        )


LOCAL_DIR = pick_download_dir()

# Snowflake connection
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "ADISHARMA")
SNOWFLAKE_ACCOUNT = os.getenv(
    "SNOWFLAKE_ACCOUNT", "oc33285.eu-central-1"
)

repo_secret_key = (
    Path(__file__).resolve().parent.parent / "secrets" / "rsa_key.p8"
)
if os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH"):
    SNOWFLAKE_PRIVATE_KEY_PATH = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
elif repo_secret_key.is_file():
    SNOWFLAKE_PRIVATE_KEY_PATH = str(repo_secret_key)
elif Path("/opt/airflow/secrets/rsa_key.p8").is_file():
    SNOWFLAKE_PRIVATE_KEY_PATH = "/opt/airflow/secrets/rsa_key.p8"
else:
    SNOWFLAKE_PRIVATE_KEY_PATH = "/opt/airflow/secrets/rsa_key.p8"

SNOWFLAKE_PRIVATE_KEY_PASSWORD = os.getenv(
    "SNOWFLAKE_PRIVATE_KEY_PASSWORD"
)

SNOWFLAKE_WAREHOUSE = os.getenv(
    "SNOWFLAKE_WAREHOUSE", "ZOMATO_WH"
)
SNOWFLAKE_DB = os.getenv("SNOWFLAKE_DB", "ZOMATO")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "RAW")

STAGE_NAME = "MINIO_ZOMATO_UPLOAD"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. CONNECT TO MINIO
# --------------------------------------------------

def create_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(
            signature_version="s3v4",
            connect_timeout=10,
            read_timeout=60,
            retries={"max_attempts": 3}
        )
    )


# --------------------------------------------------
# 3. DOWNLOAD FILES FROM MINIO
# --------------------------------------------------

def download_from_minio(s3):
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    ensure_free_space(LOCAL_DIR, required_mb=512)

    paginator = s3.get_paginator("list_objects_v2")
    downloaded_files = []

    for page in paginator.paginate(Bucket=BUCKET):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            # Ignore folder marker objects.
            if key.endswith("/"):
                continue

            # Preserve the original object directory structure.
            local_file = (LOCAL_DIR / key).resolve()

            # Prevent object keys from writing outside LOCAL_DIR.
            if not local_file.is_relative_to(LOCAL_DIR):
                raise ValueError(f"Unsafe MinIO object key: {key}")

            local_file.parent.mkdir(
                parents=True, exist_ok=True
            )

            # Fail early with a clear message instead of crashing mid-write.
            ensure_free_space(local_file.parent, required_mb=256)

            logger.info("Downloading MinIO object: %s", key)

            try:
                # Windows os.rename fails when the destination already exists.
                local_file.unlink(missing_ok=True)
                s3.download_file(
                    BUCKET, key, str(local_file)
                )
            except OSError as exc:
                raise OSError(
                    f"Failed to download {key} to {local_file}. "
                    f"Check free disk space or set LOCAL_DIR to a larger drive."
                ) from exc

            downloaded_files.append((key, local_file))

    logger.info(
        "Downloaded %d files from bucket %s",
        len(downloaded_files), BUCKET
    )

    return downloaded_files


# --------------------------------------------------
# 4. CONNECT TO SNOWFLAKE USING RSA KEY-PAIR AUTH
# --------------------------------------------------

def create_snowflake_connection():
    if not Path(SNOWFLAKE_PRIVATE_KEY_PATH).is_file():
        raise FileNotFoundError(
            "Snowflake private key not found inside the "
            f"runtime: {SNOWFLAKE_PRIVATE_KEY_PATH}"
        )

    connection_args = {
        "user": SNOWFLAKE_USER,
        "account": SNOWFLAKE_ACCOUNT,
        "private_key_file": SNOWFLAKE_PRIVATE_KEY_PATH,
        "warehouse": SNOWFLAKE_WAREHOUSE,
        "database": SNOWFLAKE_DB,
        "schema": SNOWFLAKE_SCHEMA,
    }

    if SNOWFLAKE_PRIVATE_KEY_PASSWORD:
        connection_args["private_key_file_pwd"] = (
            SNOWFLAKE_PRIVATE_KEY_PASSWORD
        )

    return snowflake.connector.connect(**connection_args)


# --------------------------------------------------
# 5. CREATE INTERNAL STAGE AND UPLOAD FILES
# --------------------------------------------------

def upload_to_snowflake(connection, downloaded_files):
    uploaded_count = 0

    with connection.cursor() as cursor:
        cursor.execute(
            f"CREATE STAGE IF NOT EXISTS {STAGE_NAME}"
        )

        # Upload each file to a matching directory
        # within the internal stage.
        for key, local_file in downloaded_files:
            parent_prefix = key.rpartition("/")[0]

            stage_location = f"@{STAGE_NAME}"
            if parent_prefix:
                stage_location += "/" + parent_prefix

            # Escape apostrophes in the local file URI.
            file_uri = local_file.as_uri().replace("'", "''")

            put_sql = (
                f"PUT '{file_uri}' {stage_location} "
                "AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
            )

            logger.info(
                "Uploading %s to Snowflake stage",
                key
            )

            cursor.execute(put_sql)
            results = cursor.fetchall()

            for result in results:
                logger.info("PUT result: %s", result)

            uploaded_count += 1

    logger.info(
        "Uploaded %d files to @%s",
        uploaded_count, STAGE_NAME
    )

    return uploaded_count


# --------------------------------------------------
# 6. VERIFY STAGE CONTENTS
# --------------------------------------------------

def verify_stage(connection):
    with connection.cursor() as cursor:
        cursor.execute(f"LIST @{STAGE_NAME}")

        results = cursor.fetchall()

        logger.info("Files visible in Snowflake stage:")

        for row in results:
            logger.info("%s", row)

        logger.info(
            "Verification complete: %d stage objects found",
            len(results)
        )

        return results


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

def main():
    connection = None

    try:
        logger.info("Connecting to MinIO...")
        s3 = create_minio_client()

        s3.head_bucket(Bucket=BUCKET)
        logger.info("MinIO bucket access verified.")
        downloaded_files = download_from_minio(s3)
        if not downloaded_files:
            logger.warning(
                "No files found in bucket %s. Nothing to upload.",
                BUCKET
            )
            return

        logger.info("Connecting to Snowflake...")
        connection = create_snowflake_connection()
        logger.info("Snowflake connection successful.")

        uploaded_count = upload_to_snowflake(
            connection, downloaded_files
        )

        stage_objects = verify_stage(connection)

        logger.info(
            "Pipeline finished. Uploaded %d files; "
            "%d objects currently visible in stage.",
            uploaded_count, len(stage_objects)
        )

    except Exception:
        logger.exception("MinIO-to-Snowflake transfer failed.")
        raise

    finally:
        if connection is not None:
            connection.close()
            logger.info("Snowflake connection closed.")


if __name__ == "__main__":
    main()

