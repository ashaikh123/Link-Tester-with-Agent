from faker import Faker
import time

fake = Faker()

def answer_question(question_text: str, profile: dict) -> str:
    q_lower = question_text.lower()
    print(f"Getting answer - for {q_lower}")
    #time.sleep(2)
    if 'age' in q_lower or 'how old are you' in q_lower:
        return str(profile['age'])
    elif 'postcode' in q_lower:
        return str(profile['au_postcode'])
    elif 'gender' in q_lower:
        return profile['gender'].capitalize()
    elif 'income' in q_lower:
        return f"${profile['income']}"
    elif 'city' in q_lower or 'live' in q_lower:
        return profile['city']
    elif 'education' in q_lower:
        return profile['education']
    elif 'job' in q_lower:
        return profile['job']
    elif 'describe yourself' in q_lower:
        return f"I'm a {profile['age']}-year-old {profile['gender']} living in {profile['city']} and working as a {profile['job']}."
    else:
        print("generating fake sentance")
        return fake.sentence(nb_words=12)
