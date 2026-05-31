from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider


def get_llm_provider(
    provider: str,
    api_key: str,
    model: str | None = None,
) -> BaseLLMProvider:
    provider = provider.lower()
    defaults = {
        "openai": "gpt-4o",
        "anthropic": "claude-sonnet-4-6",
        "gemini": "gemini-1.5-pro",
    }
    resolved_model = model or defaults.get(provider, "")

    if provider == "openai":
        return OpenAIProvider(api_key=api_key, model=resolved_model)
    elif provider == "anthropic":
        return AnthropicProvider(api_key=api_key, model=resolved_model)
    elif provider == "gemini":
        return GeminiProvider(api_key=api_key, model=resolved_model)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Choose from: openai, anthropic, gemini")
