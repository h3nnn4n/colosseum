#!/bin/bash

N_CORES=$(grep -c ^processor /proc/cpuinfo)
N_CORES=${N_CORES:-2}

echo "Starting ${N_CORES} workers"

for i in `seq "${N_CORES}"`; do
  while [[ true ]]; do python -m poetry run python tournament_online.py; done &
  sleep 1
done

echo Done
