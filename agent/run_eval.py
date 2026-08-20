import csv
import time
from run import run_episode

def run_eval_set(questions, session, max_iterations=7, out_path="eval_results.csv"):
    """
    questions: list of dicts, each {"id": int, "goal": str, "ground_truth": str}
    Runs each through run_episode, logs result, writes CSV incrementally
    (so a crash mid-run doesn't lose earlier results).
    """
    fieldnames = ["id", "goal", "ground_truth", "final_answer",
                  "termination_reason", "turn_count", "trace_summary"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for q in questions:
            print(f"Running Q{q['id']}: {q['goal']}")

            state = run_episode(
                goal=q["goal"],
                session=session,
                max_iterations=max_iterations
            )

            trace_summary = " -> ".join(
                f"{r.action}({r.action_input})" for r in state.trace
            )

            row = {
                "id": q["id"],
                "goal": q["goal"],
                "ground_truth": q["ground_truth"],
                "final_answer": state.final_answer,
                "termination_reason": state.termination_reason,
                "turn_count": len(state.trace),
                "trace_summary": trace_summary,
            }
            writer.writerow(row)
            f.flush()  # write immediately, don't lose progress on crash

            print(f"  -> {state.termination_reason}, answer={state.final_answer}")

    print(f"Done. Results in {out_path}")