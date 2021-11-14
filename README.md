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
- Open format using json for data representation and stdin / stdout to communicate
- Sample agents
- Python SDK
- Sample game
- Replay Renderer
- Headless mode

## Planned

- Swiss tournament format
- Bracket tournament format
- Website to register and upload bots
- Automated runner to download agents and play a match with them
- Persistent elo ratings
- Seasons
- Downloadable replays

# LICENSE

All files in this repository are released under [MIT](LICENSE) license, unless
explicitly noted.
