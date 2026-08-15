class TurnRecord:
    
    def __init__(self, turn_number: int, reasoning: str, action: str, 
                 action_input: dict, raw_observation, candidate_judgements: list[dict] | None ):
        
        self.turn_number = turn_number
        self.reasoning = reasoning
        self.action = action
        self.action_input = action_input
        self.raw_observation = raw_observation
        self.candidate_judgements = candidate_judgements

class EpisodeState:
    
    def __init__(self, goal: str, max_iterations: int, trace: list[TurnRecord],
                 surfaced_by, read_by, turn_number: int = 0,
                 final_answer: str | None = None, termination_reason: str | None = None):
        self.goal = goal
        self.max_iterations = max_iterations
        self.trace = trace
        self.surfaced_by = surfaced_by
        self.read_by = read_by
        self.turn_number = turn_number
        self.final_answer = final_answer
        self.termination_reason = termination_reason
    

        
        
        