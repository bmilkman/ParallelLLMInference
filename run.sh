#!/bin/bash

# Number of GPUs available
NUM_GPUS=7
PORT=5000

for (( i=0; i<$NUM_GPUS; i++ ))
do
    echo "Starting server for GPU $i on port $((PORT+i))"
    CUDA_VISIBLE_DEVICES=$i uvicorn app:app --host 0.0.0.0 --port $((PORT+i)) --workers 1 &
    sleep 2
done
uvicorn server:app --port 8008
# Wait for all processes to finish
wait

