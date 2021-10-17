
from random import randrange


def generate_random_acc():
    from random import randint
    n = 10
    range_start = 10**(n-1)
    range_end = (10**n)-1
    accountNumber = randint(range_start, range_end)
    return 'ACC' + str(accountNumber)

def choose_random_bank_branch():
    import random

    banks = [
        'UBA',
        'CalBank',
        'EcoBank',
        'Stanbic',
        'ADB'
    ]

    branch = [
        'Madina',
        'Kasoa',
        'Legon',
        'Dodowa'
    ]

    return banks[random.randint(0, 4)] + '-' + branch[random.randint(0, 3)]