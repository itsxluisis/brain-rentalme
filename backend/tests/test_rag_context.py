"""Regression tests for the RAG context-building bug: knowledge blocks were
truncated to 300 chars before being handed to the LLM, gutting the value of
the retrieved knowledge. These tests guard against reintroducing that bug and
verify the new minimum-similarity threshold behavior.
"""

from app.rag.service import build_context_prompt
from app.shared.config import settings


def _make_result(content: str, score: float = 0.9) -> dict:
    return {
        "block_id": "00000000-0000-0000-0000-000000000001",
        "entity_type": "property",
        "entity_id": "00000000-0000-0000-0000-000000000002",
        "entity_name": "Konk Hostel",
        "block_type": "faq",
        "title": "Check-in procedure",
        "content_preview": content,
        "score": score,
    }


def test_build_context_prompt_includes_full_content_over_300_chars():
    """A block longer than the old 300-char cutoff must appear in full in the
    prompt sent to the LLM (up to the configured high ceiling)."""
    long_content = "A" * 1200  # well above the old 300-char truncation
    results = [_make_result(long_content)]

    prompt = build_context_prompt(results, "How does check-in work?")

    assert long_content in prompt, "Full block content must reach the LLM context, not a 300-char slice"
    assert len(long_content) > 300


def test_build_context_prompt_empty_results_still_instructs_no_hallucination():
    """When no result clears the similarity threshold, semantic_search returns
    an empty list; the prompt must still carry the anti-hallucination
    instruction so the model says the info isn't in context instead of
    guessing."""
    prompt = build_context_prompt([], "Some unrelated question")

    assert "no está en el contexto" in prompt
    assert "CONTEXTO RELEVANTE" in prompt


def test_rag_context_char_limit_is_a_high_ceiling_not_a_snippet():
    """The configured ceiling must be generous (not a UI-preview-sized value
    like the old 300), while still bounded to protect the context window."""
    assert settings.RAG_MAX_CONTEXT_CHARS >= 1000
    assert settings.RAG_MAX_CONTEXT_CHARS <= 8000


def test_rag_min_similarity_threshold_is_configured():
    """A minimum similarity threshold must exist so irrelevant top-K filler
    is dropped instead of forced into the prompt."""
    assert 0.0 < settings.RAG_MIN_SIMILARITY < 1.0
