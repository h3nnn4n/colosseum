# Archtecture

This is the planned archtecture. Where we want to go, not were we are.

## Website

An website where the users can register and manage their Agents. Each user can
have multiple agents. Each agent will have a unique name, and optionally a
version. Internally each agent will have an unique internal id. This id
will be used to track matches, tournaments, results and ranking.

## Tournament Runner

A tournament consists of one or more matches. A tournament is defined by a set
of participants, a game, configurations for the game and a set of
configurations for the tournament itself (such as number of rounds for round
robin).

The tournament program will issue a list of matches to be run. The results of
these matches will be stored and used to rank the participants, as well a
update the ratings.

A program will be used to run each match. It will as input have a set that
defines which agents are participating (probably a list of agent ids). It will
download the agents taking part in the match, boot the game and run the game
with the participants. When finishing the result of the game will be persisted
on a database, along with a replay.

## Colosseum

Colosseum is the framework that runs the tournaments. It has skirmishes, which
are one of matches of participants on a game, matches, which are units of a
tournament, and tournaments, which are a set of matches between participants.

The goal of colosseum is to be modular and allow multiple games, with different
rules to be used to rank different agents.
