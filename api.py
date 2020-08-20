# This file provides some easy-to-use API functions for generating learning curves

from profile_generate import ProfileGenerator as PGen
from exprcontr import expr_pcontr
from random import randint
from random import choices

def gen_synthetic_anshist(n_question):
    """Generate synthetic answering history for a user with regard to questions belonging to a specific concept.

    Args:
        n_question (int): Number of questions the user has done.
    """
    assert(n_question > 0)

    # Generate a synthetic user profile
    profile = PGen.gen_profile()
    records = []

    for _ in range(n_question):
        prob_contr = expr_pcontr(records)
        cmpindex = profile.compound_index

        # base:             25%                             => pure guess
        # experience:       25%                             => the more times the user has done questions with similar concepts,
        #                                                      the more likely s/he would successfully solve it
        # compound index:   40%                             => the higher level of education the user has received,
        #                                                      the more likely s/he would be able to solve it
        # luck:             10%                             => whether or not the user is lucky enough to guess out the right answer

        tot_prob = 0.25 * 1 + 0.25 * prob_contr + 0.40 * cmpindex + 0.10 * randint(0, 1)
        ans_correct = choices([True, False], weights=[tot_prob, 1 - tot_prob])[0]

        records.append(ans_correct)

    return records, profile


def main():
    n_trial = 10
    n_question = 20

    for i in range(n_trial):
        records, profile = gen_synthetic_anshist(n_question)
        records_fh = records[:n_question // 2]
        records_lh = records[n_question // 2:]
        score = len(list(filter(lambda r: r, records))) / len(records)
        score_fh = len(list(filter(lambda r: r, records_fh))) / len(records_fh)
        score_lh = len(list(filter(lambda r: r, records_lh))) / len(records_lh)
        print(f"{'>' * 25} Iteration {i+1} {'<' * 25}")
        print(f"profile: {profile.__dict__}")
        print(f"cmpindex: {profile.compound_index}")
        print(f"records: {records}")
        print(f"score: {score}")
        print(f"score (first half): {score_fh}")
        print(f"score (last half): {score_lh}")
        print()

if __name__ == '__main__':
    main()