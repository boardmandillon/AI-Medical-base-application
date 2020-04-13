"""AAP questions and possible answers, each with a corresponding ID."""
AAP_QUESTIONS = {
    "sex": {
        "answers": {
            "male": 1,
            "female": 2,
        },
        "required": True,
        "mutually exclusive": True,
    },
    "age": {
        "answers": {
            "<10": 3,
            "10s": 4,
            "20s": 5,
            "30s": 6,
            "40s": 7,
            "50s": 8,
            "60s": 9,
            "70+": 10,
        },
        "required": True,
        "mutually exclusive": True,
    },
    "site of pain at onset": {
        "answers": {
            "right upper quadrant": 11,
            "left upper quadrant": 12,
            "right lower quadrant": 13,
            "left lower quadrant": 14,
            "upper half": 15,
            "lower half": 16,
            "right side": 17,
            "left side": 18,
            "central": 19,
            "general": 20,
            "right loin": 21,
            "left loin": 22,
            "no pain": 23,
        },
        "mutually exclusive": True,
    },
    "site of pain at present": {
        "answers": {
            "right upper quadrant": 24,
            "left upper quadrant": 25,
            "right lower quadrant": 26,
            "left lower quadrant": 27,
            "upper half": 28,
            "lower half": 29,
            "right side": 30,
            "left side": 31,
            "central": 32,
            "general": 33,
            "right loin": 34,
            "left loin": 35,
            "no pain": 36,
        },
        "required": True,
        "mutually exclusive": True,
    },
    "aggravating factors": {
        "answers": {
            "movement": 37,
            "coughing": 38,
            "respiration": 39,
            "food": 40,
            "other": 41,
            "none": 42,
        },
    },
    "relieving factors": {
        "answers": {
            "lying still": 43,
            "vomiting": 44,
            "antacids": 45,
            "food": 46,
            "other": 47,
            "none": 48,
        },
    },
    "progress": {
        "answers": {
            "better": 49,
            "same": 50,
            "worse": 51,
        },
        "mutually exclusive": True,
    },
    "duration": {
        "answers": {
            "<12 hours": 52,
            "12-23 hours": 53,
            "24-48 hours": 54,
            "2-7 days": 55,
        },
        "mutually exclusive": True,
    },
    "type": {
        "answers": {
            "intermittent": 59,
            "steady": 60,
            "colicky": 61,
        },
        "mutually exclusive": True,
    },
    "severity": {
        "answers": {
            "moderate": 63,
            "severe": 64,
        },
        "mutually exclusive": True,
    },
    "nausea": {
        "answers": {
            "yes": 65,
            "no": 66,
        },
        "mutually exclusive": True,
    },
    "vomiting": {
        "answers": {
            "yes": 67,
            "no": 68,
        },
        "mutually exclusive": True,
    },
    "anorexia": {
        "answers": {
            "yes": 69,
            "no": 70,
        },
        "mutually exclusive": True,
    },
    "previous indigestion": {
        "answers": {
            "yes": 71,
            "no": 72,
        },
        "mutually exclusive": True,
    },
    "jaundice": {
        "answers": {
            "yes": 73,
            "no": 74,
        },
        "mutually exclusive": True,
    },
    "bowels": {
        "answers": {
            "normal": 75,
            "constipation": 76,
            "diarrhoea": 77,
            "blood": 78,
            "mucus": 79,
        },
    },
    "micturition": {
        "answers": {
            "normal": 80,
            "frequency": 81,
            "dysuria": 82,
            "dark": 83,
            "haematuria": 84
        },
    },
    "previous similar pain": {
        "answers": {
            "yes": 85,
            "no": 86,
        },
        "mutually exclusive": True,
    },
    "previous abdo surgery": {
        "answers": {
            "yes": 87,
            "no": 88,
        },
        "mutually exclusive": True,
    },
    "drugs for abdo pain": {
        "answers": {
            "yes": 89,
            "no": 90,
        },
        "mutually exclusive": True,
    },
    "mood": {
        "answers": {
            "normal": 91,
            "distressed": 92,
            "anxious": 93,
        },
        "mutually exclusive": True,
    },
    "colour": {
        "answers": {
            "normal": 94,
            "pale": 95,
            "flushed": 96,
            "jaundiced": 97,
            "cyanosed": 98,
        },
    },
    "abdo movement": {
        "answers": {
            "normal": 99,
            "poor": 100,
            "peristalsis": 101,
        },
        "mutually exclusive": True,
    },
    "scar": {
        "answers": {
            "yes": 102,
            "no": 103,
        },
        "mutually exclusive": True,
    },
    "distension": {
        "answers": {
            "yes": 104,
            "no": 105,
        },
        "mutually exclusive": True,
    },
    "site of tenderness": {
        "answers": {
            "right upper quadrant": 106,
            "left upper quadrant": 107,
            "right lower quadrant": 108,
            "left lower quadrant": 109,
            "upper half": 110,
            "lower half": 111,
            "right side": 112,
            "left side": 113,
            "central": 114,
            "general": 115,
            "right loin": 116,
            "left loin": 117,
            "no pain": 118,
        },
        "mutually exclusive": True,
    },
    "rebound": {
        "answers": {
            "yes": 119,
            "no": 120,
        },
        "mutually exclusive": True,
    },
    "guarding": {
        "answers": {
            "yes": 121,
            "no": 122,
        },
        "mutually exclusive": True,
    },
    "rigidity": {
        "answers": {
            "yes": 123,
            "no": 124,
        },
        "mutually exclusive": True,
    },
    "mass": {
        "answers": {
            "yes": 125,
            "no": 126,
        },
        "mutually exclusive": True,
    },
    "murphy": {
        "answers": {
            "positive": 127,
            "negative": 128,
        },
        "mutually exclusive": True,
    },
    "bowel": {
        "answers": {
            "normal": 129,
            "decreased": 130,
            "hyper": 131,
        },
        "mutually exclusive": True,
    },
    "rectal tenderness": {
        "answers": {
            "left": 132,
            "right": 133,
            "general": 134,
            "mass": 135,
            "none": 136,
        },
    },
}

"""AAP Gynaecological questions and possible answers, 
each with a corresponding ID.
"""
AAP_GYN_QUESTIONS = {
    "periods": {
        "answers": {
            "not started": 137,
            "ceased": 138,
            "regular": 139,
            "irregular": 140,
        },
        "mutually exclusive": True,
    },
    "last monthly period": {
        "answers": {
            "normal": 141,
            "late/overdue": 142,
        },
        "mutually exclusive": True,
    },
    "vaginal discharge": {
        "answers": {
            "yes": 143,
            "no": 144,
        },
        "mutually exclusive": True,
    },
    "pregnancy": {
        "answers": {
            "impossible": 145,
            "possible": 146,
            "confirmed": 147,
        },
        "mutually exclusive": True,
    },
    "faint/dizzy": {
        "answers": {
            "yes": 148,
            "no": 149,
        },
        "mutually exclusive": True,
    },
    "previous history of salpingitis/std": {
        "answers": {
            "yes": 150,
        },
    },
    "vaginal tenderness": {
        "answers": {
            "normal": 151,
            "right": 152,
            "left": 153,
            "cervix": 154,
            "general": 155,
            "mass": 156,
            "blood (clots)": 157,
        },
    },
}
AAP_GYN_QUESTIONS.update(AAP_QUESTIONS)
