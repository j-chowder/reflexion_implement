import json
import re
from groq import Groq

client = Groq()  

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are answering a research question by searching a document corpus.

You must respond with a JSON object only, no other text, matching this schema:
{
  "reasoning": "<what you still need to find out, and why you're taking this action>",
  "action": "search" | "read_doc" | "final_answer",
  "action_input": {...},
  "candidate_judgments": [{"doc_id": "...", "verdict": "read"|"discard", "justification": "..."}] or null
}

Rules:
- action_input for "search" is {"query": "<your search string>"}
- action_input for "read_doc" is {"doc_id": "<id>"}
- action_input for "final_answer" is {"answer": "<your answer>"}
- candidate_judgments is REQUIRED and non-null only on the turn immediately after you receive
  search results: you must judge EVERY candidate returned, including ones you plan to discard.
  Explain why each discarded doc is likely irrelevant, not just that you're skipping it.
- Search results are NOT pre-filtered for relevance. Some will be distractors. Judging
  distractors correctly is part of what's being evaluated here.
- Do not call read_doc on a doc_id you have not seen in a prior search result.
"""
def _extract_prev_search_doc_ids(messages):
    """If the last message is a formatted search-result observation, return its doc_ids."""
    if not messages:
        return None
    last = messages[-1]
    if last["role"] != "user" or not last["content"].startswith("Search results for"):
        return None
    return set(re.findall(r"\[(\w+)\]", last["content"]))

def actor_step(messages, max_retries=2):
    """
    messages: list of {"role": ..., "content": ...} — full conversation so far,
    NOT including the system prompt (added here).
    Returns a parsed dict matching the schema, or raises after retries exhausted.
    """
    required_doc_ids = _extract_prev_search_doc_ids(messages)
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    last_error = None

    for attempt in range(max_retries + 1):
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=full_messages,
         #   response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content

        try:
            parsed = json.loads(raw_text)
            _validate_schema(parsed, required_doc_ids)
            return parsed
        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            full_messages = full_messages + [
                {"role": "assistant", "content": raw_text},
                {"role": "user", "content": f"That response was invalid: {e}. Return ONLY valid JSON matching the schema, nothing else."}
            ]

    raise RuntimeError(f"actor_step failed after {max_retries + 1} attempts: {last_error}")


def _validate_schema(parsed, required_doc_ids=None):
    required = {"reasoning", "action", "action_input"}
    missing = required - parsed.keys()
    if missing:
        raise ValueError(f"missing required fields: {missing}")
    if parsed["action"] not in ("search", "read_doc", "final_answer"):
        raise ValueError(f"invalid action: {parsed['action']}")
    if "candidate_judgments" not in parsed:
        parsed["candidate_judgments"] = None

    if required_doc_ids:
        cj = parsed.get("candidate_judgments")
        if not cj:
            raise ValueError(
                f"candidate_judgments required after search, got null. "
                f"Must judge: {sorted(required_doc_ids)}"
            )
        judged_ids = {j.get("doc_id") for j in cj}
        missing_ids = required_doc_ids - judged_ids
        if missing_ids:
            raise ValueError(f"candidate_judgments missing doc_ids: {sorted(missing_ids)}")
        
if __name__ == "__main__":
    messages = [{"role": "user", "content": "Goal: find who founded Iron Town. Begin."}]
    result = actor_step(messages)
    print(result)
