from state import EpisodeState, TurnRecord
from build_prompt import build_prompt
from step import actor_step

def run_episode(goal, session, max_iterations = 5):
    
    state = EpisodeState(goal=goal, max_iterations=max_iterations, trace=[],
                          surfaced_by={}, read_by={})
    
    while state.turn_number < max_iterations:
        state.turn_number += 1
        
        prompt = build_prompt(state)
        response = actor_step(prompt)
        
        record = TurnRecord(turn_number=state.turn_number, reasoning=response["reasoning"],
                             action=response["action"], action_input=response["action_input"],
                             raw_observation=None, candidate_judgements=response.get("candidate_judgements"))
        
        if response["action"] == "final_answer":
            state.final_answer = response["action_input"]["answer"]
            state.termination_reason = "final_answer_emitted"
            state.trace.append(record); break
            
        elif response["action"] == "search":
            results = session.search(response["action_input"]["query"])
            record.raw_observation = results
            for r in results:
                state.surfaced_by.setdefault(r["doc_id"], []).append(response["action_input"]["query"])
            state.trace.append(record)
            
        elif response["action"] == "read_doc":
          try:
            content = session.read_doc(response["action_input"]["doc_id"])
          except ValueError as e:
            content = {"error": str(e)}
          record.raw_observation = content
          state.read_by.setdefault(response["action_input"]["doc_id"], []).append(state.turn_number)
          state.trace.append(record)
            
    if state.termination_reason is None:
        state.termination_reason = "max_iterations_hit"
        
    return state

from session import Session

if __name__ == "__main__":
    session = Session()
    state = run_episode(
        goal="What year was Iron Town's founder killed?",
        session=session,
        max_iterations=7
    )
    print(state.termination_reason)
    print(state.final_answer)
    for r in state.trace:
      print(r.turn_number, r.action, r.action_input, r.candidate_judgements)

