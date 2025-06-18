from learning_rules import LEARNING_LOGIC, DURATION_DAYS

def calculate_units(level, daily_capacity, duration):
    try:
        return LEARNING_LOGIC[level][daily_capacity][duration]
    except KeyError:
        return 5  # default fallback