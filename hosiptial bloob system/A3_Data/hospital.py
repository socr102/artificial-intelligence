from random import choice
def check_demand():
    blgroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'X']
    return choice(blgroups)
