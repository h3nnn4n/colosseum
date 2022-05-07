# Colosseum

An modular AI playground where agents are put in a multiple scenarios to
compete each other. Automated tournaments are supported, with rankins by score
(wins are 1 point and draws are 0.5) and ELO ratings. Agents can be implemented
in any language, as long as they are able to parse json payloads and
communicate via stdin and stdout.

Currently the project is in an early stage and many things are subject to
breaking changes. Nevertheless, it is in an state where it is ready to use
and have fun.

## Features

- Round robin tournament formats
- Seasons with multiple tournaments
- Open format using json for data representation and stdin / stdout to communicate
- Sample agents
- Python SDK
- Sample games
- Replay visualization tool
- Headless mode
- Website to interact with the automated tournament system
  - Register and upload new agents
  - Persistent elo ratings
  - Download replays or watch them in the browser
- Automated runner to run tournament matches

## Environment

The project is spread across multiple repositories:
- [Tournament Engine](https://github.com/h3nnn4n/colosseum)
- [Website / API](https://github.com/h3nnn4n/colosseum_website)
- [Sample Agents](https://github.com/h3nnn4n/colosseum_agents)
- [Replay Renderer](https://github.com/h3nnn4n/colosseum_renderer)
- [Agent SDK](https://github.com/h3nnn4n/colosseum_sdk)
- [Infra](https://github.com/h3nnn4n/colosseum_infra)

# Running locally

- Setup `poetry`
- Run `poetry install`
- `poetry run python tournament.py agents/foo agent/bar agent/qux` runs a
  tournament with the given agents. The arguments must be a path to the agent
  executable file.
- `poetry run python skirmish.py agents/foo agent/bar` to run a skirmish with
  the given agents.

# LICENSE

All files in this repository are released under [MIT](LICENSE) license, unless
explicitly noted.
