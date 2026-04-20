echo '#!/bin/bash' > entrypoint.sh
echo 'set -e' >> entrypoint.sh
echo 'python manage.py migrate --noinput' >> entrypoint.sh
echo 'python manage.py collectstatic --noinput' >> entrypoint.sh
echo 'exec gunicorn _core.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 300 --keepalive 5' >> entrypoint.sh

git add entrypoint.sh _core/settings.py
git commit -m "fix: disable browser-reload in prod, increase timeout"
git push
