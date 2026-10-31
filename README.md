# Zomato End-to-End Data Engineering

An end-to-end data engineering project that demonstrates how Zomato-style
restaurant, menu, customer, order, and review data can be collected, streamed,
stored, loaded into Snowflake, and transformed into analytics-ready models with
dbt.

The repository brings together a FastAPI data source, Kafka producer and
consumer, MinIO object storage, Snowflake loading utilities, Apache Airflow
orchestration, and a dbt warehouse project. It is intended as a learning and
portfolio project; it is not affiliated with Zomato.

## Architecture

```text
CSV datasets
    |
    v
FastAPI paginated endpoints  --->  Kafka producer
                                      |
                                      v
                                Kafka topics
                                      |
                                      v
                            Kafka consumer
                                      |
                                      v
                          MinIO bronze bucket
                                      |
                         MinIO-to-Snowflake loader
                                      |
                                      v
                               Snowflake RAW
                                      |
                                  dbt build
                                      |
                         STAGING views -> MARTS
```

The components can be run independently. The current producer and consumer
configurations enable the `users` category only. The daily `zomato_batch`
Airflow DAG currently runs `dbt build`; its Snowflake `COPY INTO` raw-load
operator is present in the DAG source but commented out. The separate
MinIO-to-Snowflake utility is available in `infra/dags/`, but must be
configured and invoked as part of your own ingestion workflow.

## What is included

| Area | Purpose |
| --- | --- |
| `data/` | CSV datasets used by the local API |
| `Codebase/api/API_Dev.py` | Paginated FastAPI endpoints for the CSV datasets |
| `producer/producer.py` | Fetches API pages and publishes them to Kafka |
| `Consumer/consumer.py` | Consumes Kafka messages and writes JSON objects to MinIO |
| `infra/docker-compose.yaml` | Local Kafka, Kafdrop, MinIO, and Airflow services |
| `infra/dags/` | Airflow batch DAG and MinIO/Snowflake transfer utility |
| `dbt_zomato/` | dbt sources, staging models, dimensional models, marts, and tests |

The dbt project builds staging views and mart tables, including order and
order-item facts, customer/food/restaurant/date dimensions, daily city revenue,
delivery SLA, and restaurant performance.

## Requirements

- Python 3.10 or newer
- Docker Desktop with Docker Compose
- A Snowflake account and a warehouse/database configured for this project
- A Snowflake key-pair credential for the Snowflake transfer/dbt workflows

Install the Python dependencies from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the API locally

From the repository root:

```powershell
uvicorn Codebase.api.API_Dev:app --reload
```

The interactive API documentation is available at
<http://127.0.0.1:8000/docs>. Endpoints accept `page` (starting at 1) and
`limit` (1-1000), for example:

```text
http://127.0.0.1:8000/api/orders/?page=1&limit=100
http://127.0.0.1:8000/api/restaurant/?page=2&limit=100
```

Available routes are `/api/food/`, `/api/menu/`, `/api/order_items/`,
`/api/restaurant/`, `/api/users/`, `/api/reviews/`, and `/api/orders/`.
Password values are excluded from the users response.

## Run the local streaming services

Start Kafka and MinIO from the `infra` directory:

```powershell
cd infra
docker compose up -d zookeeper kafka kafdrop minio
```

Kafdrop is available at <http://localhost:9000>. MinIO's console is at
<http://localhost:9003> and its S3 endpoint is `http://localhost:9002`.
Create the `zomato-bronze-transaction` bucket in MinIO before starting the
consumer. The compose file currently configures local development credentials;
change them before using this setup outside a trusted local environment.

In separate terminals, from the repository root, start the producer and
consumer:

```powershell
python producer/producer.py
python Consumer/consumer.py
```

Both scripts currently connect to Kafka on `localhost:29092`, and are
configured to use the deployed API URL and the `users` category. Edit their
configuration before use if you want to point them at a local API or enable
additional categories. The consumer writes one JSON object per Kafka message
to the MinIO bucket.

## Configure Snowflake and run dbt

1. Provide your own Snowflake private key and dbt profile. Keep the profile,
   private key, and any passphrases outside version control. The expected
   profile directory for the containerized dbt task is `infra/secrets/`.
2. Configure the `dbt_zomato` profile to use your Snowflake account, user,
   warehouse, database, schema, and key-pair authentication. The dbt project
   expects the raw source tables in the `ZOMATO.RAW` schema.
3. From `dbt_zomato/`, validate and build the project:

   ```powershell
   dbt debug --profiles-dir ..\infra\secrets
   dbt build --profiles-dir ..\infra\secrets --no-partial-parse
   ```

The Airflow `zomato_batch` DAG is scheduled daily and executes the equivalent
dbt build inside the Airflow container. The compose setup builds the image and
mounts the dbt project and secrets directory:

```powershell
cd infra
docker compose up -d --build
```

Airflow is available at <http://localhost:8080>. Complete the Airflow and
Snowflake profile configuration before enabling the DAG. Starting the Airflow
services alone does not populate Snowflake's raw tables.

See [`dbt_zomato/README.md`](dbt_zomato/README.md) for the dbt model layers and
commands.

## Repository hygiene and credentials

Do not commit Snowflake private keys, dbt profiles, passwords, API tokens, or
other credentials. Replace all example credentials in the Compose file before
sharing or deploying it. The root `.gitignore` excludes local secrets and
generated logs, caches, and dbt build output; already tracked files are not
removed from Git by ignore rules.

## License and data

No license is currently specified. Review the origin, terms, and redistribution
rights for the datasets and any third-party services before reusing or
redistributing them.
