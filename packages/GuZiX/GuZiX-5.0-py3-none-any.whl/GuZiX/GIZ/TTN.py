import random
def genrandint(minimal, maximal):
    return random.randint(minimal, maximal)
def shuffle(value):
    random.shuffle(value)
    return value
def ttn(text):
    return random.randint(0, len(text))
