
import random
import string

def randomAlphanumeric(size):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(size))