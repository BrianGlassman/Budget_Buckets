import re as _imported_re

#TODO replace with named tuple or custom class so keys aren't just strings
#TODO save off as a file (JSON needs lots of formatting and custom re parser)

# Regex notes:
#   \*{11} matches exactly 11 asterisks
templates = [
    # Utilities / Rent
    {#//Phone
        'old': {'desc':'SPRINT *WIRELESS         800-639-6111 KS'},
        'new': {'category': 'Utilities', 'split': 30}},
    {#//PECO
        'old': {'desc': _imported_re.compile('^PECOENERGY       UTIL_BIL   \*{11}')},
        'new': {'category': 'Utilities', 'split': 30}},
    {#//PGW
        'old': {'desc': _imported_re.compile('^PGW WEBPAY       UTILITY    \*{11}')},
        'new': {'category': 'Utilities', 'split': 30}},
    {#//Internet
        'old': {'desc': 'VERIZON          PAYMENTREC ***********0001'},
        'new': {'category': 'Utilities', 'split': 30}},
    {#//Aritom water bill
        'old': {'desc': 'ARITOM PROPERTIES        610-353-4925 PA',
                'value': -40},
        'new': {'category': 'Utilities', 'split': 30}},
    {#//Aritom rent
        'old': {'desc': 'ARITOM PROPERTIES        610-353-4925 PA',
                'value': -1650},
        'new': {'category': 'Rent', 'split': 30}},
    {#//Aritom rent and water bill
        'old': {'desc': 'ARITOM PROPERTIES        610-353-4925 PA',
                'value': -1690},
        'new': [{'value': -1650, 'category': 'Rent', 'split': 30},
                {'value': -40, 'category': 'Utilities', 'split': 30}]},

    # Banking
    {#//CC Payments
        'old': {'desc': _imported_re.compile('^USAA CREDIT CARD PAYMENT*')},
        'new': {'category': 'CC Payments', 'split': 1}},
    {#//Cash rewards credit
        'old': {'desc': 'CASH REWARDS CREDIT',
                'value': (0, 20)},
        'new': {'category': 'Income - Other', 'split': 1}},
    {#//Interest
        'old': {'desc': 'INTEREST PAID',
                'value': (0, 5)},
        'new': {'category': 'Income - Other', 'split': 1}},

    # Other
    {#//Grubhub
        'old': {'desc': _imported_re.compile('^PAYPAL \*GRUBHUBFOOD')},
        'new': {'category': 'Food - nice', 'split': 1}},
    {#//Salary
        'old': {'desc': _imported_re.compile('^AGUSTAWESTLAND P DIRECT DEP \*{11}'),
                # TODO add entries for other pay rates, with dates
                'value': (1902.79, 1902.81)},
        'new': {'category': 'Salary', 'split': 14}},
    {#//Spotify
        'old': {'desc': 'PAYPAL           INST XFER  ***********USAI',
                'value': -10.81},
        'new': {'desc': 'Spotify --- PAYPAL           INST XFER  ***********USAI',
                'category': 'Entertainment - Other', 'split': 30}},
    {#//Car note
        'old': {'desc': _imported_re.compile('^HONDA PMT        8004489307 \*{11}'),
                'value': -320},
        'new': {'category': 'Car - Note', 'split': 30}},
    {#//Insurance
        'old': {'desc': 'USAA P&amp;C INT     AUTOPAY    ***********1608'},
        'new': {'category': 'Car/Rental Insurance', 'split': 30}},
]

# Helper functions to check different fields
def __check_desc(record, pattern) -> bool:
    """Assumes that pattern contains a desc field"""
    mask = pattern['desc']
    desc = record.desc
    if isinstance(mask, _imported_re.Pattern):
        # Regex matching (None if no match found)
        return mask.search(desc) is not None
    elif isinstance(mask, str):
        # Exact string matching
        return desc == mask
    else:
        raise NotImplementedError("Unknown mask type")
def __check_value(record, pattern) -> bool:
    """Assumes that pattern contains a value field"""
    mask = pattern['value']
    if isinstance(mask, (int, float)):
        # Exact value matching
        return self.value == mask
    else:
        # Range matching
        assert len(mask) == 2
        assert mask[0] < mask[1]
        return mask[0] <= record.value <= mask[1]

# Mapping from field name to helper function
_checker = {'desc': __check_desc,
            'value': __check_value,
            }

def match_templates(record):
    """Check against the common templates. Return whichever template
    matches, or None if no match"""

    matched = None
    # Check the transaction against all templates in order
    for template in templates:
        pattern = template['old']
        match = True
        # Run the checker for each field that has a pattern, break if any fail
        for key in pattern:
            if not _checker[key](record, pattern):
                match = False
                break

        if match:
            # Template matched, stop searching
            matched = template
            break
    return matched