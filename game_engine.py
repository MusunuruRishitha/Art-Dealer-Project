import random

class GameSession:
    def __init__(self, level):
        self.level = level
        self.deck = self.build_deck()
        random.shuffle(self.deck)
        self.market = self.deck[:12]
        self.pattern = self.pick_pattern()

    def build_deck(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = ["ace","2","3","4","5","6","7","8","9","10","jack","queen","king"]
        return [f"{r}_of_{s}" for s in suits for r in ranks]

    def restart_round(self):
        random.shuffle(self.deck)
        self.market = self.deck[:12]
        self.pattern = self.pick_pattern()

    # ------------------------------
    def pick_pattern(self):
        patterns = self.patterns_for_level()
        if not patterns:
            return None
        # Filter patterns to only those that are achievable using the current market
        possible = []
        # we'll test the pattern functions against combinations of 4 cards from market
        from itertools import combinations
        for name, func in patterns.items():
            try:
                found = False
                # avoid checking all combos if market is large — but market is typically 12
                for combo in combinations(self.market, 4):
                    try:
                        if func(combo):
                            found = True
                            break
                    except Exception:
                        # treat function error as not matching
                        continue
                if found:
                    possible.append(name)
            except Exception:
                continue
        if not possible:
            # no achievable patterns found
            return None
        return random.choice(possible)

    # ------------------------------
    def patterns_for_level(self):
        base = {
            "all red": lambda cards: all("hearts" in c or "diamonds" in c for c in cards),
            "all black": lambda cards: all("clubs" in c or "spades" in c for c in cards),
            "all hearts": lambda cards: all("hearts" in c for c in cards),
            "all spades": lambda cards: all("spades" in c for c in cards),
			"all diamonds": lambda cards: all("diamonds" in c for c in cards),
			"all clubs": lambda cards: all("clubs" in c for c in cards),
            "all queens": lambda cards: all("queen" in c for c in cards),
            "all kings": lambda cards: all("king" in c for c in cards),
			"all jacks": lambda cards: all("jack" in c for c in cards),
            "all aces": lambda cards: all("ace" in c for c in cards),
            
        }
        if self.level in ["3-5", "6-8"]:
            base.update({
                "sum to 9": lambda cards: sum(self.value(c) for c in cards) == 9,
                "ace and a black jack": lambda cards: any("ace" in c for c in cards) and any(("jack_of_spades" in c or "jack_of_clubs" in c) for c in cards),
                "all single-digit primes": lambda cards: all(self.value(c) in [2, 3, 5, 7] for c in cards),
                "all face cards": lambda cards: all(any(x in c for x in ["jack", "queen", "king"]) for c in cards),
                "all even values": lambda cards: all(self.value(c) % 2 == 0 for c in cards),
			"all odd values": lambda cards: all(self.value(c) % 2 == 1 for c in cards),
				
            })
        
        if self.level == "6-8":
            base.update({
            "sum to 21": lambda cards: sum(self.value(c) for c in cards) == 21,
            "all face cards of same color": lambda cards: (all(("hearts" in c or "diamonds" in c) for c in cards) or all(("clubs" in c or "spades" in c) for c in cards)) and all(any(x in c for x in ["jack", "queen", "king"]) for c in cards),
            "all multiples of 3": lambda cards: all(self.value(c) % 3 == 0 for c in cards),
            "all red face cards": lambda cards: all((("hearts" in c or "diamonds" in c) and any(x in c for x in ["jack", "queen", "king"])) for c in cards),
            "all black aces": lambda cards: all((("clubs" in c or "spades" in c) and "ace" in c) for c in cards),
			})

        return base

    # ------------------------------
    def value(self, card):
        # card names are like 'ace_of_hearts' or '10_of_clubs'
        rank = card.split("_")[0]
        # map written ranks to numeric values
        rank_map = {
            "ace": 1,
            "jack": 10,
            "queen": 10,
            "king": 10
        }
        if rank in rank_map:
            return rank_map[rank]
        try:
            return int(rank)
        except ValueError:
            return 0

    # ------------------------------
    def play_turn(self, selected):
        chosen = [self.market[i] for i in selected]
        if not self.pattern:
            return False, "no_pattern"
        func = self.patterns_for_level().get(self.pattern)
        if not func:
            return False, "no_pattern"
        try:
            result = func(chosen)
            return (bool(result), "")
        except Exception as e:
            # if a pattern function errors, treat as no valid pattern
            return False, "no_pattern"

    def make_guess(self, guess_name):
        return guess_name == self.pattern
