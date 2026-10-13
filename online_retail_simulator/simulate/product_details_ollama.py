"""Product details generation using Ollama (local LLM)."""

import json

import pandas as pd
import requests

from ..quality import calculate_quality_score

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"
DEFAULT_BATCH_SIZE = 5
MAX_ATTEMPTS = 3
# A 5-product batch is ~600 tokens; on CPU llama3.2 generates ~4 tokens/s, so a batch takes 2-3 minutes.
# The token cap stops a runaway generation; a truncated reply fails to parse and is retried.
MAX_TOKENS = 1536
REQUEST_TIMEOUT = 600

PROMPT_TEMPLATE = """You are a JSON generator. Generate product details for these e-commerce products.
Your response must be ONLY valid JSON - no explanations, no code, no markdown.

Products:
{products_json}

For each product, add these fields:
- title: Product title (50-100 chars)
- description: Product description (100-300 chars)
- brand: Realistic brand name
- features: List of 3-5 features

IMPORTANT: Your response must start with [ and end with ]. Do not include ```json or any other text."""


def _load_prompt_template(prompt_path: str) -> str:
    """Load a custom prompt template from a file."""
    with open(prompt_path, "r") as f:
        return f.read()


def _parse_batch(response_text: str) -> list:
    """Parse an Ollama response into a list of product dicts.

    JSON mode guarantees valid JSON but not its shape: models often wrap the list
    in an object such as ``{"products": [...]}`` or return a single product object.
    """
    parsed = json.loads(response_text)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        lists = [v for v in parsed.values() if isinstance(v, list) and all(isinstance(item, dict) for item in v)]
        if len(lists) == 1:
            return lists[0]
        if "title" in parsed:
            return [parsed]
    raise ValueError(f"Unexpected response shape: {response_text[:200]}")


def _generate_batch(prompt: str, model: str, ollama_url: str) -> list:
    """Request one batch from Ollama, retrying when the response does not parse."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"num_predict": MAX_TOKENS},
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        response_text = response.json().get("response", "")
        try:
            return _parse_batch(response_text)
        except ValueError:  # json.JSONDecodeError is a ValueError
            if attempt == MAX_ATTEMPTS:
                raise


def simulate_product_details_ollama(
    products_df: pd.DataFrame,
    model: str = DEFAULT_MODEL,
    ollama_url: str = OLLAMA_URL,
    prompt_path: str = None,
) -> pd.DataFrame:
    """Generate product details using Ollama (local LLM).

    Args:
        products_df: Input products with product_identifier, category, price
        model: Ollama model to use (default: llama3.2)
        ollama_url: Ollama API URL (default: http://localhost:11434)
        prompt_path: Optional path to custom prompt template file.
            Template should contain {products_json} placeholder.

    Returns:
        DataFrame with added title, description, brand, features
    """
    # Load custom prompt or use default
    prompt_template = _load_prompt_template(prompt_path) if prompt_path else PROMPT_TEMPLATE

    results = []
    products = products_df.to_dict("records")

    for i in range(0, len(products), DEFAULT_BATCH_SIZE):
        batch = products[i : i + DEFAULT_BATCH_SIZE]
        prompt = prompt_template.format(products_json=json.dumps(batch, indent=2))

        batch_results = _generate_batch(prompt, model, ollama_url)
        for result in batch_results:
            result["quality_score"] = calculate_quality_score(result)
        results.extend(batch_results)

    return pd.DataFrame(results)
