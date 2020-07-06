from uuid import uuid4
from scipy.stats import beta, norm
import random
from profile import Profile

# User ID, Age, Education Level, Base IQ, Base Memory Index

class ProfileGenerator:

    @staticmethod
    def gen_profile():
        userid = ProfileGenerator.gen_userid()
        age = ProfileGenerator.gen_age()
        education = ProfileGenerator.gen_education()
        baseiq = ProfileGenerator.gen_baseiq()
        basemidx = ProfileGenerator.gen_basemidx()
        profile = Profile(userid, age, education, baseiq, basemidx)
        return profile

    @staticmethod
    def gen_userid():
        return str(uuid4())

    @staticmethod
    def gen_age():
        age_min, age_max = 15, 60
        # Assume that the RV Age is a beta continuous random variable
        a, b = 2, 5
        v = beta.rvs(a, b)
        return int(v * (age_max - age_min) + age_min)

    @staticmethod
    def gen_education():
        # There are 3 education levels:
        # college, grad school, phd
        # Each education level corresponds to one integer, from 1 to 3
        # Each education level has a different probability
        # College     = 0.55
        # Grad School = 0.35
        # PhD         = 0.10
        return random.choices((1, 2, 3), (0.55, 0.35, 0.10))[0]

    @staticmethod
    def gen_baseiq():
        # According to Wikipedia, the IQ distribution across the world has mean=100 and standard deviation=15
        iq_mean, iq_std = 100, 15
        return int(norm.rvs(iq_mean, iq_std))

    @staticmethod
    def gen_basemidx():
        mm_mean, mm_std = 100, 20
        return int(norm.rvs(mm_mean, mm_std))
