# Defines logic for how many hours per day and how many units based on learning profile

LEARNING_LOGIC = {
    'basic': {
        '1-2 hours': {
            'one-week': 7,
            'one-month': 30,
            'three-months': 90
        },
        'part-time': {
            'one-week': 14,
            'one-month': 60,
            'three-months': 180
        },
        'full-time': {
            'one-week': 40,
            'one-month': 160,
            'three-months': 480
        }
    },
    'broader': {
        '1-2 hours': {
            'one-week': 6,
            'one-month': 25,
            'three-months': 75
        },
        'part-time': {
            'one-week': 12,
            'one-month': 50,
            'three-months': 150
        },
        'full-time': {
            'one-week': 35,
            'one-month': 140,
            'three-months': 420
        }
    },
    'profound': {
        '1-2 hours': {
            'one-week': 5,
            'one-month': 20,
            'three-months': 60
        },
        'part-time': {
            'one-week': 10,
            'one-month': 40,
            'three-months': 120
        },
        'full-time': {
            'one-week': 30,
            'one-month': 120,
            'three-months': 360
        }
    }
}

# For fallback unit estimation if needed
DURATION_DAYS = {
    'one-week': 7,
    'one-month': 30,
    'three-months': 90
}