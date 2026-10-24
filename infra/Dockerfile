FROM apache/airflow:2.9.3

USER root
RUN python -m venv /opt/dbt-venv \
    && chown -R airflow:root /opt/dbt-venv

USER airflow
RUN /opt/dbt-venv/bin/pip install --no-cache-dir \
    dbt-core==1.12.5 \
    dbt-snowflake==1.12.1

ENV PATH="/opt/dbt-venv/bin:${PATH}"
