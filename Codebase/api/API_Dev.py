import pandas as pd
from fastapi import FastAPI, Query
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

app = FastAPI()


def get_paginated_data(
    file_name: str,
    page: int,
    limit: int,
    exclude_columns: list[str] | None = None
):
    """
    Read a CSV in chunks and return only the requested page.
    """

    if page < 1:
        return {"error": "page must be greater than or equal to 1"}

    if limit < 1 or limit > 1000:
        return {"error": "limit must be between 1 and 1000"}

    file_path = DATA_DIR / f"{file_name}.csv"

    if not file_path.exists():
        return {"error": f"File not found: {file_name}.csv"}

    try:

        # Read only 'limit' rows at a time
        chunks = pd.read_csv(
            file_path,
            chunksize=limit
        )

        target_chunk = None

        for current_page, chunk in enumerate(chunks, start=1):

            if current_page == page:
                target_chunk = chunk
                break

        if target_chunk is None:
            return {
                "page": page,
                "limit": limit,
                "data": []
            }

        if exclude_columns:
            target_chunk = target_chunk.drop(
                columns=exclude_columns,
                errors="ignore"
            )

        target_chunk = target_chunk.where(
            pd.notnull(target_chunk),
            None
        )

        return {
            "page": page,
            "limit": limit,
            "data": target_chunk.to_dict(orient="records")
        }

    except Exception as e:

        return {
            "error": str(e)
        }


@app.get("/api/food/")
def get_food_data(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000)
):
    return get_paginated_data(
        "food",
        page,
        limit
    )


@app.get("/api/menu/")
def get_menu_data(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000)
):
    return get_paginated_data(
        "menu",
        page,
        limit
    )


@app.get("/api/order_items/")
def get_order_items_data(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000)
):
    return get_paginated_data(
        "order_items",
        page,
        limit
    )


@app.get("/api/restaurant/")
def get_restaurant_data(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000)
):
    return get_paginated_data(
        "restaurant",
        page,
        limit
    )


@app.get("/api/users/")
def get_users_data(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000)
):
    return get_paginated_data(
        "users",
        page,
        limit,
        exclude_columns=["password"]
    )


@app.get("/api/reviews/")
def get_reviews_data(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000)
):
    return get_paginated_data(
        "reviews",
        page,
        limit
    )