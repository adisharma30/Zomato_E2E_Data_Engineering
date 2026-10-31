# dbt Zomato warehouse

This dbt project transforms the Zomato raw tables in Snowflake into a
testable, analytics-ready warehouse. It uses the `dbt_zomato` profile and
expects source tables in the `ZOMATO.RAW` schema.

## Model layers

### Sources and staging

`models/staging/_sources.yml` declares the raw `restaurants`, `reviews`,
`users`, `food`, `order_items`, `menu`, and `orders` source tables.
`models/staging/` contains one staging model per source. Staging models are
configured as views in the `STAGING` schema.

### Marts

`models/marts/` contains the dimensional and analytical tables. Mart models
are configured as tables in the `MARTS` schema:

- Dimensions: customers, dates, food, and restaurants
- Facts: orders and order items
- Reporting marts: daily city revenue, delivery SLA, and restaurant
  performance

Schema tests are declared alongside the source and model definitions. The
project also has a `tests/` directory for future singular SQL tests.

## Configure your Snowflake profile

Create `infra/secrets/profiles.yml` locally and configure a `dbt_zomato`
profile with a Snowflake target. Use your own account, user, warehouse,
database, schema, and key-pair credential values. Do not commit the profile,
private key, or any passphrase. The profile directory is mounted into the
Airflow containers at `/opt/airflow/secrets`.

The profile must be available to dbt as the `dbt_zomato` profile, and the
configured Snowflake role must be able to read the declared raw source tables
and create the staging and marts schemas and models.

## Useful commands

Run these commands from the `dbt_zomato/` directory:

```powershell
dbt debug --profiles-dir ..\infra\secrets
dbt ls --profiles-dir ..\infra\secrets
dbt build --profiles-dir ..\infra\secrets --no-partial-parse
```

`dbt build` runs applicable models and tests in dependency order. Use
`dbt test --profiles-dir ..\infra\secrets` to run tests independently.

The daily Airflow DAG in `infra/dags/zomato_batch.py` runs dbt build from the
container. Its raw `COPY INTO` task is currently commented out, so raw source
tables must already be loaded before the dbt DAG can build successfully.

## Project configuration

- `dbt_project.yml`: model paths, profile name, and staging/mart materializations
- `models/staging/_sources.yml`: Snowflake raw source declarations
- `models/staging/_staging.yml`: staging model tests
- `models/marts/_marts.yml`: mart model tests
- `macros/generate_schema_name.sql`: custom target schema naming behavior
- `target/` and `logs/`: generated dbt artifacts (not source files)
