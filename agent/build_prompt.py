import json
import re
from groq import Groq

client = Groq()  

MODEL = "openai/gpt-oss-120b"

def build_prompt(state) -> list[dict]:
    """
    Serializes the full episode trace into a messages list for actor_step.
    Full history, no truncation (per current decision — revisit if token
    cost becomes a real constraint, not before).
    """
    messages = [
        {"role": "user", "content": f"Goal: {state.goal}\n\nBegin."}
    ]

    for record in state.trace:
        # the model's own prior turn, as it produced it
        assistant_payload = {
            "reasoning": record.reasoning,
            "action": record.action,
            "action_input": record.action_input,
            "candidate_judgements": record.candidate_judgements,
        }
        messages.append({"role": "assistant", "content": json.dumps(assistant_payload)})

        # the observation that resulted, formatted as readable text
        observation_text = _format_observation(record)
        messages.append({"role": "user", "content": observation_text})

    return messages


def _format_observation(record) -> str:
    
    if record.action == "search":
        results = record.raw_observation  # assumed: list[{"doc_id", "score", "topic"}]
        lines = [f'Search results for "{record.action_input["query"]}":']
        for i, r in enumerate(results, 1):
            lines.append(f'{i}. [{r["doc_id"]}] score={r["score"]:.2f} - "{r["topic"]}" - "{r['text']}"')
        return "\n".join(lines)

    elif record.action == "read_doc":
            content = record.raw_observation
            return f'Contents of [{content["doc_id"]}] (topic: {content["topic"]}):\n"""\n{content["text"]}\n"""'

    elif record.action == "final_answer":
        return "Episode ended: final answer submitted."

    return f"Unrecognized action result: {record.raw_observation}"