# Colosseum protocol

## Ping

All payloads with a key named `ping` must reply with a key named `pong` in the
next payload. This usually is the first message and will contain only it, and
it serves as a sanity check that the communication protocol is working. It may
be possible that this happens during gameplay, as a simple heart beat, and it
must be responded. Failing to comply may cause the agent to be marked as dead /
crashed.

## Agent ID

All agents are going to receive an `agent-id` which will be used to identify
itself and other agents in the world. This happens before the simulation
starts.  A payload containing `set_agent_id` means that the agent must store
the value of this key internally and use it in all further communications, by
adding a key named `agent_id` and using the value from `set_agent_id` as the
value. Failure to comply will result in the payload being ignored.

The key usually will be an uuid, but under some circumstances it may be a human
readable string, such as `foo bar` or `protomegalovirus`, limited to 255
characters long.

## World State

During gameplay the agents will receive a key named `world_state`. The contents
are specific to the game being played and will vary. A separate documentation
will be provided for each game.

## Actions

After the agent receiving a world state it must return a set of actions, which
may be empty. The payload must be in the following format:
```json
{
  "agent_id": agent_id,
  "actions": [
    actions_here
  ]
}
```

The exact content of the `actions` key will vary from game to game, but it will
always be a list of objects. Documentation for it will be provided on a per
game basis.

The `agent_id` must always be the agent id given
to the agent before the world simulation starts. Invalid values will be
ignored.  Attempting to spoof and using another agent id will be automatically
flagged as cheating and the agent will be disqualified.

## End of game instruction

When the simulation ends the agent will receive a key named `stop` in the
payload.  The value will be an object with a key `reason`, the values can be
will be the reason, which may be `end_of_game` or `cheating_detected`.
Additional keys may be provided on an per game basis, and will be documented
separatelly.
