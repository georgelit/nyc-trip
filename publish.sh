#!/bin/sh
# Публикует страницу поездки в Нью-Йорк. Пример: ./publish.sh "переставили вечер пятницы"
exec python3 "$(dirname "$0")/tools/publish.py" "$@"
