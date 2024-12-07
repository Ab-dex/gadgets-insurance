import random
import string

def generate_secret(length=4):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))