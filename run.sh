#!/bin/bash
export FLASK_APP=service
export SOURCES_PORT=8000
export SERVICE_PORT=8001

flask run --port $SOURCES_PORT &
SOURCES_PID=$!

flask run --port $SERVICE_PORT

kill -TERM $SOURCES_PID