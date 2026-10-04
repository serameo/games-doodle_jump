"""Scoring (rules 2.3): collecting coins and diamonds.

Coins are worth 1 point, diamonds are worth 3 (both defined on the
Collectible subclasses in game/collectible.py). Pickup is a simple
rectangle overlap with the player - no falling/landing condition, unlike
platform collision - since you can grab a collectible mid-air.
"""

from game.player import Player


class Score:
    def __init__(self) -> None:
        self.value = 0

    def add(self, points: int) -> None:
        self.value += points


def collect_collectibles(player: Player, collectibles: list, score: Score) -> list:
    """Check the player against every collectible; add points for any
    that overlap and return the list of collectibles still remaining
    (the ones picked up this call are dropped)."""
    player_rect = player.rect
    remaining = []
    for item in collectibles:
        if player_rect.colliderect(item.rect):
            score.add(item.VALUE)
        else:
            remaining.append(item)
    return remaining
