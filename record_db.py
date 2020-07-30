from random import choice, randint, random, choices
from datetime import datetime, timedelta
import json
from common import OptionDiffLevel
from exprcontr import expr_pcontr

# Each record of a user consists of the following info
# Record = ConceptIDs, DifficultyLevel, CorrectAnswer, UserAnswer, TimeSpent, SubmitTimeStamp

class RecordDB:

    def __init__(self, profiles, concepts, questions):
        self.__profiles = profiles
        self.__concepts = concepts
        self.__questions = questions

        self.__profile_dict = { p.id: p for p in profiles }
        self.__question_dict = { q[0]: q for q in questions }

        self.__record_database = { p.id: {} for p in self.__profiles }              # key=question id, value=Records
        self.__concept_database = { p.id: {} for p in self.__profiles }             # key=concept id, value=[True/False, ...]
        self.__time_database = { p.id: None for p in self.__profiles }              # value=timestamp of the last time the user solving a question
        self.__concept_correlations = dict()                                        # key=concept id, value= {concept id, correlation value}

    @staticmethod
    def answering(correctness, answer):
        if correctness:
            return answer
        else:
            option_set = list('ABCD')
            option_set.remove(answer)
            return choice(option_set)

    def concept_correlate(self, cpt_a, cpt_b, cv):
        if cpt_a not in self.__concepts:
            raise ValueError(f"Concept {repr(cpt_a)} does not exist in RecordDB")
        if cpt_b not in self.__concepts:
            raise ValueError(f"Concept {repr(cpt_b)} does not exist in RecordDB")
        if not isinstance(cv, float) or cv < -1 or cv > 1:
            raise ValueError("Correlation value needs to be a float number within range [-1, 1]")
        if cpt_a not in self.__concept_correlations:
            self.__concept_correlations[cpt_a] = {}
        if cpt_b not in self.__concept_correlations:
            self.__concept_correlations[cpt_b] = {}
        self.__concept_correlations[cpt_a][cpt_b] = cv
        self.__concept_correlations[cpt_b][cpt_a] = cv

    def dump_records(self, filename):
        with open(filename, 'w') as f:
            for userid, user_records in self.__record_database.items():
                for question_id, question_records in user_records.items():
                    for qrecord in question_records:
                        concepts, difflevel, correct_ans, user_ans, tspent, tstamp = qrecord
                        obj = {
                            'UserID': userid,
                            'QuestionID': question_id,
                            'ConceptIDs': list(concepts),
                            'DifficultyLevel': difflevel.name,
                            'CorrectAnswer': correct_ans,
                            'UserAnswer': user_ans,
                            'TimeSpent': tspent,
                            'TimeStamp': tstamp
                        }
                        f.write(json.dumps(obj) + '\n')

    def gen_record(self, userid):
        if userid not in self.__profile_dict:
            raise ValueError(f"User profile ID={userid} does not exist")

        # Select a question
        question = choice(self.__questions)
        question_id, linked_concepts, answers = question

        # Check how many times a user has answered correctly or wrongly to a specific concepts
        concept_records = [self.__concept_database[userid][lcpt] for lcpt in linked_concepts if lcpt in self.__concept_database[userid]]

        # Select a time to do the question
        time_to_submit = None
        if self.__time_database[userid] is None:
            # Get current time
            time_to_submit = datetime.now()
        else:
            continuous = random() < 0.9     # If the user is in the process of doing multiple exercises
            last_time = datetime.fromtimestamp(self.__time_database[userid])
            microseconds_apart = randint(15, 45)
            if continuous:
                minutes_apart = randint(1, 10)
                seconds_apart = randint(1, 59)
                time_to_submit = last_time + timedelta(0, minutes_apart * 60 + seconds_apart, microseconds_apart)
            else:
                days_apart = randint(1, 30)
                hours_apart = randint(1, 23)
                minutes_apart = randint(1, 59)
                seconds_apart = randint(1, 59)
                time_to_submit = last_time + timedelta(
                    days_apart,
                    hours_apart * 60 * 60 + minutes_apart * 60 + seconds_apart,
                    microseconds_apart
                )
        to_submit_timestamp = datetime.timestamp(time_to_submit)
        to_submit_timespent = randint(0, 15) * 60 + randint(1, 59)   # in seconds

        to_submit_difflevel = choice(list(OptionDiffLevel))
        to_submit_correct_answer = answers[to_submit_difflevel]

        to_submit_user_answer = None

        # This version does not take into account when the user does the question last time
        # It only cares about how many times the user has done questions related to a specific
        # concept and whether s/he has answered correctly or not

        prob_contr = 0

        if len(concept_records) != 0:
            # Iterate over each concept and calculate its probability contribution
            for cr in concept_records:
                prob_contr += expr_pcontr(cr)
            prob_contr /= len(concept_records)

        cmpindex = self.__profile_dict[userid].compound_index

        # base:             25%                             => pure guess
        # experience:       25%                             => the more times the user has done questions with similar concepts,
        #                                                      the more likely s/he would successfully solve it
        # compound index:   40%                             => the higher level of education the user has received,
        #                                                      the more likely s/he would be able to solve it
        # luck:             10%                             => whether or not the user is lucky enough to guess out the right answer

        tot_prob = 0.25 * 1 + 0.25 * prob_contr + 0.40 *  + 0.10 * randint(0, 1)
        to_submit_correct = choices([True, False], weights=[tot_prob, 1 - tot_prob])[0]
        to_submit_user_answer = RecordDB.answering(to_submit_correct, to_submit_correct_answer)

        new_record = (
            linked_concepts,
            to_submit_difflevel,
            to_submit_correct_answer,
            to_submit_user_answer,
            to_submit_timespent,
            to_submit_timestamp
        )

        if question_id not in self.__record_database[userid]:
            self.__record_database[userid][question_id] = []
        self.__record_database[userid][question_id].append(new_record)
        for lcpt in linked_concepts:
            if lcpt not in self.__concept_database[userid]:
                self.__concept_database[userid][lcpt] = []
            self.__concept_database[userid][lcpt].append(True if to_submit_correct else False)
        self.__time_database[userid] = to_submit_timestamp
