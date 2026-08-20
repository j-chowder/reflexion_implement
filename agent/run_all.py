from session import Session
from run_eval import run_eval_set
from questions import QUESTIONS

session = Session()
run_eval_set(QUESTIONS, session, out_path="eval_results.csv")