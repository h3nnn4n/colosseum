#!/usr/bin/env python3

import itertools
from collections import defaultdict
from pathlib import Path

from simple_elo import compute_updated_ratings

from colosseum.games.food_catcher.game import World

from .match import match


INITIAL_ELO = 1200


class TournamentResult:
    def __init__(self, participants, games):
        self._games = games
        self._participants = participants

    @property
    def games(self):
        return self._games

    @property
    def participants(self):
        return self._participants

    @property
    def rankings(self):
        return self._rankings_by("score")

    @property
    def elo_rankings(self):
        return self._rankings_by("elo")

    def _rankings_by(self, key):
        ranked_participans = sorted(
            self.participants, key=lambda x: getattr(x, key), reverse=True
        )
        return {
            rank: participant for rank, participant in enumerate(ranked_participans)
        }


class Game:
    def __init__(self, *args):
        self._players = args
        self._result = None
        self._result_by_player = {}

    def set_results(self, result):
        self._result = result["scores"]

        if self.n_players != 2:
            raise RuntimeError("only pairwise matches are supported at this point")

        if self.has_winner:
            winner = self._get_player_by_agent_path(self.rankings[0]["agent_path"])
            loser = self._get_player_by_agent_path(self.rankings[1]["agent_path"])
            winner.win()
            loser.lose()

            self._update_elo(winner, loser, 1)

        if self.is_draw:
            for player in self._players:
                player.draw()

            self._update_elo(*self._players, 0.5)

    def _update_elo(self, player1, player2, result):
        elos = {player1.pretty_name: player1.elo, player2.pretty_name: player2.elo}
        match_result = {(player1.pretty_name, player2.pretty_name): result}
        updated_elos = compute_updated_ratings(elos, match_result)

        player1._update_elo(updated_elos[player1.pretty_name])
        player2._update_elo(updated_elos[player2.pretty_name])

    @property
    def n_players(self):
        return len(self._players)

    @property
    def rankings(self):
        return sorted(self._result, key=lambda x: x["score"], reverse=True)

    @property
    def is_draw(self):
        return self.rankings[0]["score"] == self.rankings[1]["score"]

    @property
    def has_winner(self):
        return self.rankings[0]["score"] > self.rankings[1]["score"]

    @property
    def winner(self):
        return self._get_player_by_agent_path(self.rankings[0]["agent_path"])

    @property
    def pretty_results(self):
        return "\n".join(
            f'{ranking["name"]} {ranking["score"]:.2f}' for ranking in self.rankings
        )

    def _get_player_by_agent_path(self, agent_path):
        for player in self._players:
            if player.agent_path == agent_path:
                return player


class Participant:
    def __init__(self, agent_path):
        self.agent_path = agent_path
        self.wins = 0
        self.loses = 0
        self.draws = 0
        self.score = 0
        self._elo = INITIAL_ELO

    def win(self):
        self.wins += 1
        self.score += 1

    def lose(self):
        self.loses += 1

    def draws(self):
        self.draws += 0
        self.score += 0.5

    def _update_elo(self, elo):
        self._elo = elo

    @property
    def elo(self):
        return self._elo

    @property
    def pretty_name(self):
        return Path(self.agent_path).stem


def round_robin(participants, n_rounds=1, n_participants_per_round=2):
    games = []

    for n_round in range(n_rounds):
        for agent_bracket in itertools.combinations(
            participants, n_participants_per_round
        ):
            print(
                f'participants: {" vs ".join([a.pretty_name for a in agent_bracket])}'
            )
            game = Game(*list(agent_bracket))

            world = World()
            game.set_results(match(world, [a.agent_path for a in agent_bracket]))
            print(game.pretty_results)
            print()

            games.append(game)

    return TournamentResult(participants, games)


def tournament(agent_paths, mode):
    participants = [Participant(agent_path) for agent_path in agent_paths]

    if mode == "ROUND_ROBIN":
        results = round_robin(participants)
    if mode == "DOUBLE_ROUND_ROBIN":
        results = round_robin(participants, n_rounds=2)
    if mode == "TRIPLE_ROUND_ROBIN":
        results = round_robin(participants, n_rounds=3)

    return results
