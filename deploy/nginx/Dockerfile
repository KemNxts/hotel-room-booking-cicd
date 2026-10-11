# Nginx reverse proxy image.
# Build from the REPO ROOT so app/static can be copied in:
#   docker build -f deploy/nginx/Dockerfile -t hotel-booking-nginx .
#
# The config is baked into the image (instead of bind-mounting it) so the same
# image works anywhere - including when Jenkins, itself running in a
# container, starts it through the host's Docker daemon.
FROM nginx:1.27-alpine

COPY deploy/nginx/hotel.conf /etc/nginx/conf.d/default.conf
# Nginx serves CSS directly; Gunicorn only handles the dynamic pages.
COPY app/static /usr/share/nginx/static
