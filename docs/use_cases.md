# Use Cases

The Online Retail Simulator addresses real-world challenges across different roles and scenarios in e-commerce and data science.

## 📊 Data Scientist: ML Model Training

**Challenge**: "I need realistic e-commerce data for testing my models without using production data"

**Solution**:
```python
from online_retail_simulator import simulate

# Generate 30 days of sales data across 8 categories
sales_df = simulate("config.yaml")
print(f"Generated {len(sales_df)} sales records for ML training")
```

**Why this matters**: Get diverse product catalogs with realistic pricing, daily sales patterns, and multiple categories - perfect for training recommendation engines, demand forecasting, or customer segmentation models.

**Benefits**:
- Privacy-safe synthetic data
- Configurable data volume and patterns
- Reproducible datasets with seed control
- Multiple product categories for diverse training scenarios

## 🧪 Product Manager: A/B Test Simulation

**Challenge**: "I want to simulate A/B test results before launching catalog enrichment experiments"

**Solution**:
```python
from online_retail_simulator import simulate, enrich

# Generate baseline data
baseline_df = simulate("simulation_config.yaml")

# Simulate enrichment impact (30% of products, 50% boost, 7-day ramp)
enriched_df = enrich("enrichment_config.yaml", baseline_df)

# Compare results
lift = (enriched_df['revenue'].sum() / baseline_df['revenue'].sum() - 1) * 100
print(f"Projected revenue lift: {lift:.1f}%")
```

**Why this matters**: Test different enrichment strategies, effect sizes, and rollout timelines before committing resources to real experiments.

**Benefits**:
- Risk-free experiment planning
- Multiple scenario testing
- Statistical power analysis
- Resource allocation optimization

## 🎓 Educator: Teaching Analytics Concepts

**Challenge**: "I need clean datasets to teach e-commerce analytics concepts to students"

**Solution**:
```bash
# Generate demo data for classroom use
python demo/run_all_demos.py

# Students get realistic data with:
# - Product catalogs (Electronics, Books, Clothing, etc.)
# - Daily sales transactions
# - Treatment effect examples
```

**Why this matters**: Provide students with realistic, privacy-safe data that demonstrates real-world e-commerce patterns and experimental design concepts.

**Benefits**:
- No privacy concerns with synthetic data
- Consistent datasets across semesters
- Real-world complexity without real-world complications
- Hands-on experience with experimental design

## 🔧 Developer: Application Testing

**Challenge**: "I need synthetic data to test my e-commerce application without production dependencies"

**Solution**:
```python
# Quick integration testing
from online_retail_simulator import simulate

# Generate test data matching your schema
sales_df = simulate("test_config.yaml")

# Use in your tests
assert len(sales_df) > 0
assert all(sales_df['revenue'] == sales_df['price'] * sales_df['quantity'])
```

**Why this matters**: Eliminate dependencies on production databases, create reproducible test scenarios, and validate your application logic with consistent synthetic data.

**Benefits**:
- No production data dependencies
- Reproducible test scenarios
- Configurable edge cases
- Fast test execution

## Advanced Use Cases

### Causal Inference Research

Researchers studying treatment effects in e-commerce can use the simulator to:
- Generate controlled datasets with known ground truth
- Test causal inference methodologies
- Validate statistical approaches before applying to real data

### Business Intelligence Development

BI teams can use synthetic data to:
- Develop and test dashboards
- Validate ETL pipelines
- Train stakeholders on new analytics tools

### Competitive Analysis Simulation

Market researchers can:
- Model competitor pricing strategies
- Simulate market response scenarios
- Test pricing optimization algorithms

### Compliance and Privacy Testing

Organizations can:
- Test data anonymization techniques
- Validate privacy-preserving analytics
- Demonstrate compliance capabilities without exposing real data

## Configuration Examples by Use Case

### Data Science Training
```yaml
SEED: 42
RULE:
  NUM_PRODUCTS: 1000
  DATE_START: "2024-01-01"
  DATE_END: "2024-12-31"
  SALE_PROB: 0.6
```

### A/B Test Planning
```yaml
SEED: 42
SYNTHESIZER:
  SYNTHESIZER_TYPE: gaussian_copula
  DEFAULT_PRODUCTS_ROWS: 500
  DEFAULT_SALES_ROWS: 10000
```

### Educational Demo
```yaml
SEED: 123
RULE:
  NUM_PRODUCTS: 50
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-07"
  SALE_PROB: 0.8
```

### Integration Testing
```yaml
SEED: 999
RULE:
  NUM_PRODUCTS: 10
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-01"
  SALE_PROB: 1.0
```
