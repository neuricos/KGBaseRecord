class Profile:

    MAX_AGE = 20

    def __init__(self, userid, age, education, baseiq, basemidx):
        self.__id = userid
        self.__age = age
        self.__education = education
        self.__baseiq = baseiq
        self.__basemidx = basemidx

    @property
    def id(self):
        return self.__id

    @property
    def age(self):
        return self.__age

    @property
    def education(self):
        return self.__education

    @property
    def current_iq(self):
        deterioration_rate = 0.003
        age_diff = abs(self.age - Profile.MAX_AGE)
        iq = self.__baseiq * pow(1 - deterioration_rate, age_diff)
        return iq

    @property
    def current_midx(self):
        deterioration_rate = 0.005
        age_diff = abs(self.age - Profile.MAX_AGE)
        midx = self.__basemidx * pow(1 - deterioration_rate, age_diff)
        return midx

    @property
    def compound_index(self):
        total = self.education * (self.current_iq + self.current_midx)
        cpd_max = 3 * (150 + 150)
        return total / cpd_max
