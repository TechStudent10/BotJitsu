import string, random

def generate_random_id(length=6):
    return "".join(random.choices(
        string.ascii_letters + string.digits,
        k=length
    ))
