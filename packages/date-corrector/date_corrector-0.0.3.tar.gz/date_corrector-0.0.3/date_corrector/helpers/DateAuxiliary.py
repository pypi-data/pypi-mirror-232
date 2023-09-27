similarChars_en = {
    '0': ['O', 'o', 'D', 'Q', 'n'],
    '1': ['l', 'I', 'i', 'L', 'j', 'J', 't', '|', '/', '\\'],
    '2': ['Z', 'z'],
    '3': ['E'],
    '4': ['R', 'A'],
    '5': ['S', 's', '$'],
    '6': ['b', 'G', 'o'],
    '7': ['T', 'J', 'Z'],
    '8': ['B'],
    '9': ['g'],
    '1/': ['V']
}
similarSeps_en = {
    '/': ['l', 'I', 'i', 'L', 'T', 'j', 'J', '|', '\\', ',', '1', '7'],
    '-': ['_'],
    '.': [' '],
    ' ': []
}
similarAlpha_en = {
    'A': ['4'],
    'B': ['8', 'R', 'D', 'E', 'F', 'P'],
    'C': ['G', 'O', 'o', '0', 'e', 'Q'],
    'D': ['G', 'R', 'B'],
    'E': ['B', 'F'],
    'F': ['T', 'P', 'E'],
    'G': ['C', 'O', 'o', '0'],
    'H': ['L', 'T', 't', 'F', 'E'],
    'I': ['l', 'T', 'Y', 'i', 'L', 'j', 'J', 't', '1', '|', '/', '\\'],
    'J': ['1', 'I', ')'],
    'L': ['l', 'T', 'i', 'I', 'j', 'J', 't', '1', '|', '/', '\\'],
    'M': ['V', 'N'],
    'N': ['W', 'K', 'V'],
    'O': ['0', 'o', 'Q', 'G', 'C'],
    'P': ['R', 'F', 'f'],
    'R': ['P', 'F', 'f'],
    'S': ['5', 's'],
    'T': ['Y', 'l', 'F', 'I', 'i', 'L', 'j', 'J', 't', '1', '|', '/', '\\'],
    'U': ['V', 'O', '0'],
    'V': ['U', 'Y', 'N', 'M'],
    'Y': ['T', 'V', 'l', 'I', 'i', 'L', 'j', 'J', 't', '1', '|', '/', '\\'],

    'a': ['g', 'o', 'e'],
    'b': ['6', 'p'],
    'c': ['e', 'C', 'G'],
    'e': ['G', 'c', 'a', 'o', 'r'],
    'g': ['9', 'a'],
    'h': ['n', 'm'],
    'i': ['I', '1', 'L', 'l', '|', '/', '\\', 't', 'j', 'J'],
    'l': ['L', '1', 'I', 'i', '|', '/', '\\', 't', 'j', 'J'],
    'm': ['n', 'h'],
    'n': ['m', 'h'],
    'o': ['0', 'O', 'a', 'e', 'u'],
    'p': ['9', 'b', 'R'],
    'r': ['f', 't', 'c', 'e'],
    's': ['S', '5'],
    't': ['l', 'L', 'j', 'J', 'f'],
    'u': ['y', 'v', 'o'],
    'v': ['y', 'u', 'x'],
    'y': ['u', 'v', 'x']
}
similarNums_en = {
    '0': ['9', '8', '6'],
    '1': ['4', '7'],
    '2': ['3', '1'],
    '3': ['8'],
    '4': ['1'],
    '5': ['6', '9'],
    '6': ['0', '6'],
    '7': ['1'],
    '8': ['9', '6', '0', '5', '3'],
    '9': ['8', '0'],
}
months_en = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',

    'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
    'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'
]
dateFormats_en = [
    'nnsnnsnnnn', 'nnnnsnnsnn', 'nnsnnsnn',

    'nsnnsnnnn', 'nnsnsnnnn', 'nsnsnnnn',
    'nsnnsnn', 'nnsnsnn', 'nsnsnn',

    'nnsaaasnnnn', 'nnsaaasnn',
    'nnsaaaaaaaaasnnnn',

    'nsaaasnnnn', 'nsaaasnn',
    'nsaaaaaaaaasnnnn'
]
possibleOrders_en = ['dmy', 'mdy', 'ymd']



similarChars_ar = {
    '٠': ['.', ',', '-', 'ء', 'ن', '،', '؛'],
    '١': ['l', 'ا', 'إ', 'أ', 'آ', 'ل', 'ر', 'ز'],
    '٢': ['ا', 'إ', 'أ', 'آ', 'ل', '؟'],
    '٣': ['ا', 'إ', 'أ', 'آ', 'ل'],
    '٤': ['ك', 'ع', 'غ', 'ح', 'خ'],
    '٥': ['o', 'ه', 'و', 'م', 'ؤ', 'ة', 'د'],
    '٦': ['ا', 'إ', 'أ', 'آ'],
    '٧': ['V', 'ل', 'ك'],
    '٨': ['ا', 'إ', 'أ', 'آ'],
    '٩': ['و', 'ف', 'ق']
}
similarSeps_ar = {
    '/': ['ا', 'إ', 'أ', 'آ', 'ل', 'ر', 'ز', '؛'],
    '-': ['_', '،'],
}
similarAlpha_ar = {
    'أ': ['ا', 'ل'],
    'ا': ['أ', 'ل'],
    'ب': ['ت', 'ن', 'ي'],
    'ت': ['ب', 'ن', 'ة'],
    'د': ['ر', 'و', 'ذ', 'ز', 'ه', 'ة'],
    'ر': ['د', 'ز', 'ذ'],
    'س': ['ت', 'ش', 'ن'],
    'ط': ['ف', 'ظ'],
    'غ': ['ف', 'ع'],
    'ف': ['ط', 'غ', 'ق'],
    'ك': ['ل', 'ح', 'خ', 'ج'],
    'ل': ['ا', 'أ', 'ك'],
    'م': ['ت', 'ن'],
    'ن': ['ب', 'ت', 'م', 'س', 'ة'],
    'و': ['ر', 'ز'],
    'ي': ['ب']
}
similarNums_ar = {
    '٠': [],
    '١': [
        '٩', '٨', '٧', '٦', '٢', '٣'
    ],
    '٢': [
        '٣', '٦', '١'
    ],
    '٣': [
        '٢', '٦', '١'
    ],
    '٤': [],
    '٥': [
        '٩'
    ],
    '٦': [
        '٩', '١'
    ],
    '٧': [
        '١'
    ],
    '٨': [
        '١'
    ],
    '٩': [
        '٦', '١'
    ]
}
months_ar = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
]
dateFormats_ar = [
    'nnsnnsnnnn',
    'nsnnsnnnn', 'nnsnsnnnn', 'nsnsnnnn',
    'nnnnsnnsnn',
    'nnnnsnnsn', 'nnnnsnsnn', 'nnnnsnsn',

    'nnnnsaaaaaasnn', 'nnsaaaaaasnnnn', 'nnnnsaaaaaasn', 'nsaaaaaasnnnn'
]
possibleOrders_ar = ['dmy', 'ymd']


aux_data = {
    'en': {
        'similarChars': similarChars_en,
        'similarAlpha': similarAlpha_en,
        'similarSeps': similarSeps_en,
        'similarNums': similarNums_en,
        'dateFormats': dateFormats_en,
        'months': months_en,
        'possibleOrders': possibleOrders_en,
    },
    'ar': {
        'similarChars': similarChars_ar,
        'similarAlpha': similarAlpha_ar,
        'similarSeps': similarSeps_ar,
        'similarNums': similarNums_ar,
        'dateFormats': dateFormats_ar,
        'months': months_ar,
        'possibleOrders': possibleOrders_ar,
    }
}