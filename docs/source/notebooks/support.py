"""Support functions for the Online Retail Simulator notebook."""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def display_product_details(product, title, add_newline=False):
    """
    Display formatted product details.

    Parameters
    ----------
    product : pandas.Series
        Product data with 'brand', 'title', 'description', and 'features' fields.
    title : str
        Header title to display above the product details.
    add_newline : bool, optional
        Whether to add a newline before the display (default: False).
    """
    if add_newline:
        print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print(f"Brand:       {product['brand']}")
    print(f"Title:       {product['title']}")
    print(f"Description: {product['description']}")
    print(f"Features:    {product['features']}")


def plot_revenue_by_category(category_revenue):
    """
    Plot horizontal bar chart of revenue by category.

    Parameters
    ----------
    category_revenue : pandas.Series
        Series with category names as index and revenue values.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    category_revenue.plot(kind="barh", ax=ax, color=sns.color_palette("viridis", len(category_revenue)))
    ax.set_xlabel("Revenue ($)")
    ax.set_ylabel("Category")
    ax.set_title("Total Revenue by Category")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    plt.show()


def plot_daily_metrics_trend(daily_metrics):
    """
    Plot daily revenue trend line chart.

    Parameters
    ----------
    daily_metrics : pandas.DataFrame
        DataFrame with 'date' and 'revenue' columns.
    """
    daily_metrics = daily_metrics.copy()
    daily_metrics["date"] = pd.to_datetime(daily_metrics["date"])

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        daily_metrics["date"],
        daily_metrics["revenue"],
        marker="o",
        linewidth=2,
        markersize=4,
    )
    ax.fill_between(daily_metrics["date"], daily_metrics["revenue"], alpha=0.3)
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue ($)")
    ax.set_title("Daily Revenue Trend")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_conversion_funnel(metrics):
    """
    Plot shopper journey conversion funnel.

    Parameters
    ----------
    metrics : pandas.DataFrame
        DataFrame with 'impressions', 'visits', 'cart_adds', and 'ordered_units' columns.
    """
    funnel_data = {
        "Impressions": metrics["impressions"].sum(),
        "Visits": metrics["visits"].sum(),
        "Cart Adds": metrics["cart_adds"].sum(),
        "Orders": metrics["ordered_units"].sum(),
    }
    stages = list(funnel_data.keys())
    values = list(funnel_data.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("Blues_r", len(stages))
    bars = ax.barh(stages[::-1], values[::-1], color=colors)
    ax.set_xlabel("Count")
    ax.set_title("Shopper Journey Funnel")

    for bar, val in zip(bars, values[::-1]):
        ax.text(
            val + max(values) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{val:,}",
            va="center",
            fontsize=10,
        )

    plt.tight_layout()
    plt.show()


def plot_treatment_effect(metrics, enriched, enrichment_start):
    """
    Plot daily revenue comparing original vs enriched data.

    Parameters
    ----------
    metrics : pandas.DataFrame
        Original metrics DataFrame with 'date' and 'revenue' columns.
    enriched : pandas.DataFrame
        Enriched metrics DataFrame with 'date' and 'revenue' columns.
    enrichment_start : str
        Date string (YYYY-MM-DD) when enrichment treatment began.
    """
    daily_original = metrics.groupby("date")["revenue"].sum().reset_index()
    daily_original["date"] = pd.to_datetime(daily_original["date"])

    daily_enriched = enriched.groupby("date")["revenue"].sum().reset_index()
    daily_enriched["date"] = pd.to_datetime(daily_enriched["date"])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        daily_original["date"],
        daily_original["revenue"],
        marker="o",
        linewidth=2,
        markersize=4,
        label="Original",
        color="#1f77b4",
    )
    ax.plot(
        daily_enriched["date"],
        daily_enriched["revenue"],
        marker="s",
        linewidth=2,
        markersize=4,
        label="Enriched",
        color="#2ca02c",
    )
    ax.axvline(
        pd.to_datetime(enrichment_start),
        color="red",
        linestyle="--",
        alpha=0.7,
        label="Treatment Start",
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue ($)")
    ax.set_title("Treatment Effect: Daily Revenue")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
