import random


def random_pick():
    """
    Just check out this function to get famous foods in Vancouver.

    Returns:
        food: str
    """
    local_dishes = [
        'B.C. roll',
        'Japadog',
        'Candied salmon',
        'Poutine',
        'Dungeness crab',
        'West Coast oysters',
        'Spot prawns',
        'Tacofino',
        'Nanaimo bar',
        'Pickleback']

    ret = random.choice(local_dishes)
    return ret


if __name__ == "__main__":
    print(random_pick())
