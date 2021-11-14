#!/usr/bin/env python3

import itertools
from collections import defaultdict
from pathlib import Path

from colosseum.games.food_catcher.game import World

from .match import match


INITIAL_ELO = 1200


class Game:
    def __init__(self, *args):
        self.players = args
        self.result = None

    @property
    def n_players(self):
        return len(self.players)

    @property
    def rankings(self):
        return sorted(self.result, key=lambda x: x["score"], reverse=True)

    @property
    def draw(self):
        scores = self.rankings.values()
        return scores[0] == scores[1]

    @property
    def has_winner(self):
        scores = self.rankings.values()
        return scores[0] > scores[1]

    @property
    def pretty_results(self):
        return "\n".join(
            f'{ranking["name"]} {ranking["score"]:.2f}' for ranking in self.rankings
        )


class Participant:
    def __init__(self, agent_path):
        self.agent_path = agent_path
        self.wins = 0
        self.loses = 0
        self.draws = 0
        self.score = 0
        self.elo = INITIAL_ELO

    def win(self):
        self.wins += 1
        self.score += 1

    def lose(self):
        self.lose += 1

    def draws(self):
        self.draws += 0
        self.score += 0.5

    @property
    def pretty_name(self):
        return Path(self.agent_path).stem


def round_robin(participants, n_rounds=1, n_participants_per_round=2):
    games = []

    for agent_bracket in itertools.combinations(participants, n_participants_per_round):
        print(f'participants: {" vs ".join([a.pretty_name for a in agent_bracket])}')
        game = Game(agent_bracket)

        world = World()
        game.result = match(world, [a.agent_path for a in agent_bracket])
        print(game.pretty_results)
        print()

    return games


def tournament(agent_paths, mode):
    participants = [Participant(agent_path) for agent_path in agent_paths]

    if mode == "ROUND_ROBIN":
        return round_robin(participants)
    if mode == "DOUBLE_ROUND_ROBIN":
        return round_robin(participants, n_rounds=2)
    if mode == "TRIPLE_ROUND_ROBIN":
        return round_robin(participants, n_rounds=3)
