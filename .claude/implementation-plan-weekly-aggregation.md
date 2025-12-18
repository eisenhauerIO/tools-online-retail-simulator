# Implementation Plan: Weekly Aggregation for Rule-Based Metrics

## Objective

Add a configurable `granularity` parameter to the rule-based metrics simulation that allows users to choose between daily or weekly aggregated output.

## User Requirements (Confirmed)

1. **Integration approach:** Config option to choose daily vs weekly output
2. **Week definition:** ISO week (Monday-Sunday), date column shows week start (Monday)
3. **Aggregation method:** Sum quantity and revenue per product per week
4. **Backward compatibility:** ❌ NOT REQUIRED - Breaking changes acceptable

## Summary of Changes

**Core principle:** Leverage the existing config system architecture where all parameters are defined in `config_defaults.yaml`, validated by `config_processor.py`, and directly accessed in simulation functions.

**Implementation decisions:**
- ✅ Default granularity: `"daily"` (more granular, users opt into weekly)
- ✅ Update all existing configs explicitly with `granularity: "daily"` for clarity
- ❌ No backward compatibility required (breaking changes OK)

**Core implementation files:**
1. ✏️ [online_retail_simulator/config_defaults.yaml](online_retail_simulator/config_defaults.yaml) - Add `granularity: "daily"` to `RULE.METRICS.PARAMS`
2. ✏️ [online_retail_simulator/simulate/metrics_rule_based.py](online_retail_simulator/simulate/metrics_rule_based.py) - Add `_aggregate_to_weekly()` and weekly logic
3. ✏️ [online_retail_simulator/tests/test_metrics_rule.py](online_retail_simulator/tests/test_metrics_rule.py) - Add weekly tests

**Existing config files to update (add explicit `granularity: "daily"`):**
4. ✏️ [online_retail_simulator/tests/config_rule.yaml](online_retail_simulator/tests/config_rule.yaml)
5. ✏️ [demo/simulate/config_default_simulation.yaml](demo/simulate/config_default_simulation.yaml)
6. ✏️ [demo/simulate/config_custom_simulation.yaml](demo/simulate/config_custom_simulation.yaml)
7. ✏️ [demo/enrich/config_default_enrichment.yaml](demo/enrich/config_default_enrichment.yaml)
8. ✏️ [demo/enrich/config_custom_enrichment.yaml](demo/enrich/config_custom_enrichment.yaml)
9. ✏️ [development/config_default_simulation.yaml](development/config_default_simulation.yaml)

**Documentation files:**
10. ✏️ [docs/configuration.md](docs/configuration.md) - Document `granularity` parameter
11. ✏️ [README.md](README.md) - Add weekly example

**New files to create:**
- ✨ `online_retail_simulator/tests/config_rule_weekly.yaml` - Test config for weekly
- ✨ `demo/simulate/run_weekly_simulation.py` - Demo comparing daily vs weekly (optional)

**Key architectural insight:**
- No need for `.get("granularity", "daily")` in simulation function
- Config system handles merging, validation, and ensures parameter exists
- Direct access `params["granularity"]` is consistent with existing code patterns

## Current Implementation Analysis

### Config Processing System

**Key Insight:** All config validation happens in [config_processor.py](online_retail_simulator/config_processor.py):

1. **Schema extraction** (lines 11-31): Extracts expected parameters from `config_defaults.yaml`
2. **Deep merge** (lines 48-67): User config merged over defaults
3. **Validation** (lines 79-117):
   - Checks for unexpected params (line 96-101)
   - Checks for missing params (line 104-108)
   - ALL params from defaults must be present after merge
4. **Simulation functions assume params exist**: They directly access `params["key"]` without `.get()` (lines 24-28 in metrics_rule_based.py)

**Critical Understanding:**
- ✅ All PARAMS defined in `config_defaults.yaml` are validated as required
- ✅ User configs are merged with defaults, so missing params get default values
- ✅ Simulation functions can safely assume all params exist (no need for `.get()` or defaults)
- ⚠️ Adding new param requires it in `config_defaults.yaml` (becomes required for validation)

### Current Metrics Implementation

**File:** [online_retail_simulator/simulate/metrics_rule_based.py](online_retail_simulator/simulate/metrics_rule_based.py)

**Current behavior:**
- Generates one row per product per day
- Date loop: `while current_date <= end_date: ... current_date += timedelta(days=1)`
- Output schema: `[asin, category, price, date, quantity, revenue]`
- Date format: String "YYYY-MM-DD"
- Returns DataFrame with all daily records (denormalized)

**Current config parameters (RULE.METRICS.PARAMS):**
```yaml
date_start: "2024-01-01"
date_end: "2024-01-31"
sale_prob: 0.7
seed: null
```

**Parameter access pattern:**
```python
params = config["RULE"]["METRICS"]["PARAMS"]
date_start, date_end, sale_prob, seed = (
    params["date_start"],  # Direct access, no .get()
    params["date_end"],
    params["sale_prob"],
    params["seed"],
)
```

## Implementation Plan

### Step 1: Update Configuration Schema

**File to modify:** [online_retail_simulator/config_defaults.yaml](online_retail_simulator/config_defaults.yaml)

**Changes:**
Add new `granularity` parameter to `RULE.METRICS.PARAMS`:

```yaml
RULE:
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-01-31"
      sale_prob: 0.7
      seed: null
      granularity: "daily"  # NEW: "daily" or "weekly"
```

**Default value:** `"daily"` (backward compatible)

---

### Step 2: Modify Rule-Based Metrics Function

**File to modify:** [online_retail_simulator/simulate/metrics_rule_based.py](online_retail_simulator/simulate/metrics_rule_based.py)

**Implementation approach:**
1. Extract params including `granularity`
2. **If weekly: Adjust date range to full week boundaries BEFORE simulation**
   - Move `date_start` back to Monday of that week
   - Move `date_end` forward to Sunday of that week
3. Generate daily data for the (possibly adjusted) date range
4. If weekly: aggregate daily data to weekly WITH zero-sale rows
5. Return aggregated DataFrame

**Key logic to add:**

```python
def simulate_metrics_rule_based(product_characteristics: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Generate synthetic daily product metrics (rule-based).
    Args:
        product_characteristics: DataFrame of product characteristics
        config: Complete configuration dictionary
    Returns:
        DataFrame of product metrics (one row per product per date, with all characteristics)
    """
    import random
    from datetime import datetime, timedelta

    params = config["RULE"]["METRICS"]["PARAMS"]
    date_start, date_end, sale_prob, seed = (
        params["date_start"],
        params["date_end"],
        params["sale_prob"],
        params["seed"],
    )
    granularity = params["granularity"]  # NEW: Direct access (validated by config_processor)

    if seed is not None:
        random.seed(seed)

    start_date = datetime.strptime(date_start, "%Y-%m-%d")
    end_date = datetime.strptime(date_end, "%Y-%m-%d")

    # NEW: For weekly granularity, adjust date range to full week boundaries
    # This ensures we generate complete weeks (Monday-Sunday) for clean aggregation
    if granularity == "weekly":
        # Move start_date back to Monday of that week
        start_date = start_date - timedelta(days=start_date.weekday())
        # Move end_date forward to Sunday of that week
        end_date = end_date + timedelta(days=(6 - end_date.weekday()))

    # Generate daily data (existing logic)
    rows = []
    current_date = start_date
    while current_date <= end_date:
        for _, prod in product_characteristics.iterrows():
            sale_occurred = random.random() < sale_prob
            if sale_occurred:
                quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                revenue = round(prod["price"] * quantity, 2)
            else:
                quantity = 0
                revenue = 0.0
            row = prod.to_dict()
            row["date"] = current_date.strftime("%Y-%m-%d")
            row["quantity"] = quantity
            row["revenue"] = revenue
            rows.append(row)
        current_date += timedelta(days=1)

    daily_df = pd.DataFrame(rows)

    # NEW: Weekly aggregation logic
    if granularity == "weekly":
        return _aggregate_to_weekly(daily_df, product_characteristics)

    return daily_df


def _aggregate_to_weekly(daily_df: pd.DataFrame, product_characteristics: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily metrics to weekly granularity using ISO weeks (Monday-Sunday).

    IMPORTANT: Includes ALL products for ALL weeks with zero sales (quantity=0, revenue=0.0).
    This ensures the weekly DataFrame has the same completeness as daily data.

    Args:
        daily_df: Daily metrics DataFrame with columns [asin, category, price, date, quantity, revenue]
        product_characteristics: Original product characteristics DataFrame

    Returns:
        Weekly aggregated DataFrame with same schema, date = week start (Monday)
    """
    import pandas as pd

    # Convert date strings to datetime for week calculation
    df = daily_df.copy()
    df['date'] = pd.to_datetime(df['date'])

    # Get ISO week start (Monday) for each date
    df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='d')

    # Get unique weeks in the date range
    unique_weeks = df['week_start'].unique()

    # Create complete product × week grid to ensure zero-sale rows are included
    products = product_characteristics[['asin', 'category', 'price']].copy()
    week_grid = pd.DataFrame({'week_start': unique_weeks})
    complete_grid = products.merge(week_grid, how='cross')

    # Aggregate actual sales by product and week
    sales_agg = df.groupby(['asin', 'category', 'price', 'week_start'], as_index=False).agg({
        'quantity': 'sum',
        'revenue': 'sum'
    })

    # Merge with complete grid to fill in zero-sale weeks
    weekly = complete_grid.merge(
        sales_agg,
        on=['asin', 'category', 'price', 'week_start'],
        how='left'
    )

    # Fill NaN values with 0 (weeks with no sales)
    weekly['quantity'] = weekly['quantity'].fillna(0).astype(int)
    weekly['revenue'] = weekly['revenue'].fillna(0.0)

    # Convert week_start back to string format YYYY-MM-DD
    weekly['date'] = weekly['week_start'].dt.strftime('%Y-%m-%d')
    weekly = weekly.drop(columns=['week_start'])

    # Reorder columns to match original schema
    weekly = weekly[['asin', 'category', 'price', 'date', 'quantity', 'revenue']]

    return weekly
```

**Important implementation details:**

1. **Date range adjustment for weekly granularity:**
   - When `granularity == "weekly"`, adjust date range BEFORE simulation:
     - Move `date_start` back to the Monday of that week
     - Move `date_end` forward to the Sunday of that week
   - Then simulate daily data for the full week-aligned range
   - Then aggregate to weekly
   - **Clear comments in code explain this adjustment**

2. **Zero-sales handling:**
   - Products with zero sales in a week MUST appear in output with `quantity=0` and `revenue=0.0`
   - Use product × week cross-join to create complete grid
   - Left merge with aggregated sales data
   - Fill NaN with zeros

3. **Why weeks spanning months is NOT an issue:**
   - By adjusting date range to week boundaries, we ensure complete weeks
   - ISO week calculation handles month/year boundaries naturally
   - No special handling needed once dates are week-aligned

---

### Step 3: Update Tests

**File to modify:** [online_retail_simulator/tests/test_metrics_rule.py](online_retail_simulator/tests/test_metrics_rule.py)

**New test cases needed:**

```python
def test_metrics_rule_weekly_granularity():
    """Test weekly aggregation produces correct output."""
    import os
    import pandas as pd
    from datetime import datetime

    # Create test config with weekly granularity
    config_path = os.path.join(os.path.dirname(__file__), "config_rule_weekly.yaml")

    products = simulate_characteristics(config_path)
    df = simulate_metrics(products, config_path)

    # Basic validations
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "asin" in df.columns
    assert "date" in df.columns
    assert "quantity" in df.columns
    assert "revenue" in df.columns

    # Weekly-specific validations
    df['date_dt'] = pd.to_datetime(df['date'])

    # All dates should be Mondays (weekday = 0)
    assert all(df['date_dt'].dt.weekday == 0), "All dates should be Mondays (ISO week start)"

    # Should have fewer rows than daily (grouped by week)
    daily_df = simulate_metrics(products, os.path.join(os.path.dirname(__file__), "config_rule.yaml"))
    assert len(df) < len(daily_df), "Weekly data should have fewer rows than daily"

    # Revenue should be sum of daily revenues (spot check)
    # ... additional validation logic ...


def test_metrics_rule_weekly_backward_compatible():
    """Test that omitting granularity parameter defaults to daily."""
    import os

    # Use existing config without granularity parameter
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")

    products = simulate_characteristics(config_path)
    df = simulate_metrics(products, config_path)

    # Should behave as daily (existing test validates this)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
```

**New test config file:** `tests/config_rule_weekly.yaml`
```yaml
RULE:
  CHARACTERISTICS:
    FUNCTION: simulate_characteristics_rule_based
    PARAMS:
      num_products: 10
      seed: 42
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-01-31"
      sale_prob: 0.7
      seed: 42
      granularity: "weekly"
```

---

### Step 4: Update Documentation

**Files to modify:**

1. **[docs/configuration.md](docs/configuration.md)** - Add granularity parameter documentation
2. **[README.md](README.md)** - Add example of weekly usage
3. **[docs/examples.md](docs/examples.md)** - Add weekly aggregation example

**Documentation content:**

```markdown
### Granularity Parameter (RULE.METRICS.PARAMS)

**Parameter:** `granularity`
**Type:** String
**Required:** No
**Default:** `"daily"`
**Options:** `"daily"` or `"weekly"`

Controls the time granularity of the output metrics data.

- `"daily"`: One row per product per day (default behavior)
- `"weekly"`: One row per product per week (ISO week, Monday-Sunday)

When `granularity: "weekly"`:
- Data is aggregated by ISO week (Monday as week start)
- `date` column shows the Monday of each week (YYYY-MM-DD format)
- `quantity` and `revenue` are summed across the week
- Only weeks with sales are included (zero-sale weeks excluded)

**Example:**
```yaml
RULE:
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-01-31"
      sale_prob: 0.7
      seed: 42
      granularity: "weekly"  # Generate weekly aggregated data
```
```

---

### Step 5: Add Demo Script (Optional)

**New file:** [demo/simulate/run_weekly_simulation.py](demo/simulate/run_weekly_simulation.py)

Demonstrate weekly aggregation with side-by-side comparison to daily data.

---

## Critical Files to Modify

1. [online_retail_simulator/config_defaults.yaml](online_retail_simulator/config_defaults.yaml) - Add `granularity: "daily"` parameter
2. [online_retail_simulator/simulate/metrics_rule_based.py](online_retail_simulator/simulate/metrics_rule_based.py) - Add aggregation logic
3. [online_retail_simulator/tests/test_metrics_rule.py](online_retail_simulator/tests/test_metrics_rule.py) - Add tests
4. [docs/configuration.md](docs/configuration.md) - Document new parameter
5. [README.md](README.md) - Add usage example

**New files:**
- `tests/config_rule_weekly.yaml` - Test configuration
- `demo/simulate/run_weekly_simulation.py` - Demo script (optional)

---

## Testing Strategy

1. **Unit tests:** Verify aggregation logic produces correct weekly sums
2. **Integration tests:** Verify end-to-end pipeline with weekly config
3. **Backward compatibility:** Verify existing configs (without granularity) still work
4. **Edge cases:**
   - Single week date range
   - Partial weeks at boundaries
   - Products with no sales in certain weeks
   - Month/year boundaries

---

## Config System Implications

### How Config Processing Works

**Config merge flow:**
1. User provides config (may omit `granularity`)
2. `config_processor.process_config()` loads defaults
3. User config deep-merged over defaults
4. Validation ensures all params from defaults are present
5. Simulation functions receive complete config with all params

**Example:**

User config:
```yaml
RULE:
  METRICS:
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-12-31"
      sale_prob: 0.8
      seed: 123
      # granularity NOT specified
```

After merge with defaults:
```yaml
RULE:
  METRICS:
    PARAMS:
      date_start: "2024-01-01"    # User value
      date_end: "2024-12-31"      # User value
      sale_prob: 0.8              # User value
      seed: 123                   # User value
      granularity: "daily"        # From config_defaults.yaml
```

### Why No `.get()` Needed

**Current pattern in all simulation functions:**
```python
# Direct access - no defaults, no .get()
date_start, date_end, sale_prob, seed = (
    params["date_start"],
    params["date_end"],
    params["sale_prob"],
    params["seed"],
)
```

**Reason:**
- `config_processor.py` validates ALL params from `config_defaults.yaml` are present
- Missing params cause `ValueError` at config load time (line 104-108)
- Simulation functions can safely assume params exist
- This is consistent across all simulation functions

**For `granularity`:**
```python
granularity = params["granularity"]  # Direct access, like other params
```

## Migration Notes

**Impact on existing users:**
- Existing configs without `granularity` parameter will fail validation after this change
- Users must add `granularity: "daily"` or `"weekly"` to their configs
- All test configs and demos are being updated to include explicit `granularity: "daily"`

**Recommended migration:**
1. Add `granularity: "daily"` to all existing user configs to maintain current behavior
2. Or add `granularity: "weekly"` to switch to weekly aggregation

---

## Future Enhancements (Out of Scope)

- Monthly aggregation (`granularity: "monthly"`)
- Custom week definitions (e.g., Sunday-Saturday)
- Additional aggregation statistics (avg, max, min, days_with_sales)
- Configurable zero-sale inclusion/exclusion
