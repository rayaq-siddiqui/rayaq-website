#!/bin/sh
# Usage: ./vmrun.sh 'remote command to run on rayaq-server'
exec gcloud compute ssh rayaq-server --project=rayaq-website --zone=us-central1-a --command="$1"
