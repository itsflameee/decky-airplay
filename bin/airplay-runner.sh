#!/usr/bin/env bash
FLAG_ACTIVE="/tmp/airplay_stream_active"

while [ -f "$FLAG_ACTIVE" ]; do
    sleep 0.5
done

exit 0