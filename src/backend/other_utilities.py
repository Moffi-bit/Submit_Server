from datetime import datetime
import random

def generate_id():
    return str(int(random.random() * random.randint(100000, 5000000) * datetime.now().microsecond))
