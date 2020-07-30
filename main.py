from uuid import uuid4
from random import randint, sample, choice
from profile_generate import ProfileGenerator as PGen
from common import OptionDiffLevel
from record_db import RecordDB

NUM_USERS = 10
NUM_CONCEPTS = 1000
NUM_QUESTIONS = 5000
QUESTION_OPTIONS = 'ABCD'

# Generate user profiles

user_profiles = tuple(PGen.gen_profile() for _ in range(NUM_USERS))

# Generate concepts

dummy_prefix = "DM - "

concepts = list(f"concept-{uuid4()}" for _ in range(NUM_CONCEPTS))

bfs = f"{dummy_prefix}Banking Financial Statement"
mfs = f"{dummy_prefix}Market Financial Statement"
netin = f"{dummy_prefix}Net Income"
exps = f"{dummy_prefix}Expenditure"

# Add some dummy concepts
concepts.extend([bfs, mfs, netin, exps])

concepts = tuple(concepts)

# Generate questions

questions = tuple(
    (
        f"question-{uuid4()}",                      # Question ID
        set(sample(concepts, randint(1, 3))),       # Linked concepts
        {
            OptionDiffLevel.EASY: choice(QUESTION_OPTIONS),
            OptionDiffLevel.MEDIUM: choice(QUESTION_OPTIONS),     # Answer for each difficulty level
            OptionDiffLevel.HARD: choice(QUESTION_OPTIONS)
        }
    )
    for _ in range(NUM_QUESTIONS)
)

rdb = RecordDB(user_profiles, concepts, questions)

for i in range(1000):
    userid = choice(user_profiles).id
    rdb.gen_record(userid)

rdb.concept_correlate(bfs, mfs, 0.7)
rdb.concept_correlate(netin, exps, -0.6)

rdb.dump_records('output.json')