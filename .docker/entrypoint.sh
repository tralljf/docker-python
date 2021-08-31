#!/bin/bash

celery -A scheduler.celery_app beat -l debug &
celery -A scheduler.celery_app worker -l info &
tail -f /dev/null
