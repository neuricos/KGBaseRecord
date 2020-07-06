from random import choice, randint, random, choices
from datetime import datetime, timedelta
import json
from common import OptionDiffLevel

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
        self.__concept_database = { p.id: {} for p in self.__profiles }             # key=concept id, value=['#Correct', '#Wrong']
        self.__time_database = { p.id: None for p in self.__profiles }              # value=timestamp of the last time the user solving a question

    @staticmethod
    def answering(correctness, answer):
        if correctness:
            return answer
        else:
            option_set = list('ABCD')
            option_set.remove(answer)
            return choice(option_set)

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

        if question_id in self.__record_database[userid]:
            qrecords = list(self.__record_database[userid][question_id])
            qr = sorted(qrecords, key=lambda r: -r[5])[0]
            time_diff = (datetime.fromtimestamp(qr[5]) - datetime.now()).total_seconds() // 60 // 60
            # If the user has done the question within a day, then s/he has 90% chance of doing it right
            if time_diff <= 24:
                to_submit_correct = choices([True, False], weights=[0.9, 0.1])[0]
                to_submit_user_answer = RecordDB.answering(to_submit_correct, to_submit_correct_answer)
            # If the user has done the question within a week, then s/he has 85% chance of doing it right
            elif time_diff <= 7 * 24:
                to_submit_correct = choices([True, False], weights=[0.85, 0.15])[0]
                to_submit_user_answer = RecordDB.answering(to_submit_correct, to_submit_correct_answer)
            # If the user has done the question within a month, then s/he has 80% chance of doing it right
            elif time_diff <= 30 * 7 * 24:
                to_submit_correct = choices([True, False], weights=[0.8, 0.2])[0]
                to_submit_user_answer = RecordDB.answering(to_submit_correct, to_submit_correct_answer)
            else:
                # Calculate the corretness of each concept and average them
                concept_records = list(filter(lambda r: r[0] != 0 or r[1] != 0, concept_records))
                concept_correctness = [cr[0] / (cr[0] + cr[1] + 1) for cr in concept_records]
                concept_correctness_avg = sum(concept_correctness) / len(concept_correctness) if len(concept_correctness) > 0 else 0.5
                # 10% -> lunk
                # 30% -> compound index
                # 30% -> record
                # 30% -> base
                prob = 0.1 * randint(0, 1) + 0.3 * self.__profile_dict[userid].compound_index + 0.3 * concept_correctness_avg + 0.3
                to_submit_correct = choices([True, False], weights=[prob, 1 - prob])[0]
                to_submit_user_answer = RecordDB.answering(to_submit_correct, to_submit_correct_answer)
        else:
            # 40% -> luck
            # 50% -> compound index
            # 10% -> base
            prob = 0.4 * randint(0, 1) + 0.5 * self.__profile_dict[userid].compound_index + 0.1
            to_submit_correct = choices([True, False], weights=[prob, 1 - prob])[0]
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
                self.__concept_database[userid][lcpt] = [0, 0]
            target_index = 0 if to_submit_correct_answer == to_submit_user_answer else 1
            self.__concept_database[userid][lcpt][target_index] += 1
        self.__time_database[userid] = to_submit_timestamp
