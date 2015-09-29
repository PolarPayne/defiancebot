from enum import Enum


class States(Enum):
    NOT_STARTED = 0
    TEAM_SELECTION = 1
    TEAM_VOTE = 2
    ON_MISSION = 3
    SPY_VICTORY = 10
    RESISTANCE_VICTORY = 11
