import pandas as pd

_months = pd.date_range("2025-01-01", periods=12, freq="MS")

revenue = pd.DataFrame(
    {
        "month": list(_months) * 4,
        "category": (
            ["Online subscriptions"] * 12
            + ["Online services"] * 12
            + ["Retail stores"] * 12
            + ["Retail partners"] * 12
        ),
        "group": ["Online revenue"] * 24 + ["Retail revenue"] * 24,
        "value": (
            [8, 9, 10, 11, 12, 13, 13, 12, 11, 10, 9, 8]
            + [4, 4, 5, 5, 6, 6, 7, 7, 6, 5, 5, 4]
            + [7, 8, 8, 9, 9, 10, 10, 9, 9, 8, 8, 7]
            + [3, 3, 4, 4, 5, 5, 6, 5, 5, 4, 4, 3]
        ),
    }
)
