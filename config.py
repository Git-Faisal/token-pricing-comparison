"""Experiment configuration: model roster and API settings.

Six flagship models, one per lab, as listed on OpenRouter on 2026-08-19.
Sticker prices recorded here are USD per token (OpenRouter pricing fields)
at config time; the experiment always uses the actual billed cost returned
by the API, never these numbers.

Open-weight models are pinned to a single hosting provider so that every
call is served (and priced) identically. Closed models have one provider.
"""

API_URL = "https://openrouter.ai/api/v1/chat/completions"
KEY_PATHS = ["../.openrouter_key", ".openrouter_key"]  # first match wins; or env OPENROUTER_API_KEY

APP_HEADERS = {
    "HTTP-Referer": "https://github.com/Git-Faisal/token-pricing-comparison",
    "X-Title": "LLM Unit Economics Experiment",
}

MODELS = [
    {
        "label": "Claude Fable 5",
        "lab": "Anthropic",
        "id": "anthropic/claude-fable-5",
        "sticker_in": 10.00,   # USD per 1M tokens
        "sticker_out": 50.00,
        "provider_pin": None,
        "public_tokenizer": None,  # not published
    },
    {
        "label": "GPT-5.6 Sol",
        "lab": "OpenAI",
        "id": "openai/gpt-5.6-sol",
        "sticker_in": 2.50,
        "sticker_out": 15.00,
        "provider_pin": None,
        "public_tokenizer": "o200k_base",  # tiktoken; assumed current OpenAI encoding
    },
    {
        "label": "Kimi K3",
        "lab": "Moonshot AI",
        "id": "moonshotai/kimi-k3",
        "sticker_in": 3.00,
        "sticker_out": 15.00,
        "provider_pin": "moonshotai",
        "public_tokenizer": None,  # weights open; HF tokenizer exists but vocab undocumented
    },
    {
        "label": "Gemini 3.1 Pro",
        "lab": "Google",
        "id": "google/gemini-3.1-pro-preview",
        "sticker_in": 2.00,
        "sticker_out": 12.00,
        "provider_pin": None,
        "public_tokenizer": None,  # not published
    },
    {
        "label": "GLM-5.3",
        "lab": "Zhipu (Z.ai)",
        "id": "z-ai/glm-5.3",
        "sticker_in": 1.40,
        "sticker_out": 4.40,
        "provider_pin": "z-ai",
        "public_tokenizer": None,  # open weights; tokenizer on HF
    },
    {
        "label": "DeepSeek V4 Pro",
        "lab": "DeepSeek",
        "id": "deepseek/deepseek-v4-pro-0813",
        "sticker_in": 0.66,   # DeepSeek's own endpoint on OpenRouter
        "sticker_out": 1.98,
        # NOTE: DeepSeek's official endpoint trains on prompt data, so
        # OpenRouter accounts exclude it unless the account's privacy
        # setting allows such providers. Enable it in OpenRouter settings,
        # or change this pin to "together" (third-party host, $1.32/$3.96).
        "provider_pin": "deepseek",
        "public_tokenizer": "deepseek",  # official pip package: deepseek-tokenizer
    },
]

# Default number of runs per (model, task). The extreme sudoku is capped
# lower because a single run can burn tens of thousands of reasoning tokens.
DEFAULT_RUNS = 3
RUNS_OVERRIDE = {"sudoku_extreme": 2}

REQUEST_TIMEOUT_S = 900
MAX_RETRIES = 3
