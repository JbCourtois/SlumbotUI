RANKS = [*range(2, 10), 'T', 'J', 'Q', 'K', 'A']
SUITS = ['d', 'h', 's', 'c']

CARDS = {}

for ri, r in enumerate(RANKS):
    for si, s in enumerate(SUITS):
        CARDS[f'{r}{s}'] = 13 * si + ri
