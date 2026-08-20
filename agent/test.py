from session import Session
from build_prompt import build_prompt
from step import actor_step
from state import TurnRecord, EpisodeState

# test = Session()

# res = test.search('Exile')

#for text in res:
#     print(test.read_doc(text['doc_id'])['topic'])
    
    


# --- fabricate a one-turn trace using the real search() output you just captured ---

search_results = [
    {'doc_id': 'tosx6u', 'score': 0.18267004922110194, 'topic': 'The Founding of The Shard',
     'text': "The Shard was officially founded in 1105 by King Vandhilt Claymore, who had been exiled from World's End by his own sister, Dahlia, and carved out a new rule in the wake of that exile."},
    {'doc_id': '85lilt', 'score': 0.17412316210520912, 'topic': 'The Overthrow of the Shadow Clan',
     'text': 'The Shadow Clan held power over Iron Town for 30 years, until the Light Clan rose against them, overthrowing their rule and driving them into exile at the Underside Peaks.'},
    {'doc_id': 'v95i55', 'score': 0.0, 'topic': 'The Split of the Shield Clan',
     'text': "In 1139, an internal division split the Shield Clan into two rival factions, the Buckler Clan and the Kite Clan. The Kite Clan chose to leave, relocating to Ogrias' Rest in the aftermath."}
]

turn_1 = TurnRecord(
    turn_number=1,
    reasoning="I need to find who was exiled and the circumstances, so I'll search for 'exile'.",
    action="search",
    action_input={"query": "exile"},
    raw_observation=search_results,
    candidate_judgements=None,   # nothing to judge yet — this record represents the turn that ISSUED the search
)

state = EpisodeState(
    goal="Who was exiled, and why?",
    max_iterations=6,
    trace=[turn_1],
    surfaced_by={},
    read_by={},
)

# --- build the prompt from that fabricated state ---
messages = build_prompt(state)

for m in messages:
    print(m["role"].upper(), "-", m["content"][:300])
    print("---")

# --- get the model's next move: it should now judge the 3 candidates ---
result = actor_step(messages)
print(result)