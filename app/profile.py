import random
from typing import Dict
from faker import Faker

fake = Faker()

def generate_profile(age_range=(18, 70), income_range=(20000, 150000)) -> Dict:
    gender = random.choice(['male', 'female'])
    au_postcode=2000
    age = random.randint(*age_range)
    income = random.randint(*income_range)
    city = random.choice(['Sydney', 'Melbourne', 'Brisbane', 'Perth'])
    education = random.choice(['High School', 'Bachelor', 'Master', 'PhD'])
    job = fake.job()

    return {
        'name': fake.name_male() if gender == 'male' else fake.name_female(),
        'au_postcode':au_postcode,
        'gender': gender,
        'age': age,
        'income': income,
        'city': city,
        'education': education,
        'job': job
    }
