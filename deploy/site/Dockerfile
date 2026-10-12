FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY index.html cetrti.json /srv/
COPY d /srv/d
COPY fonts /srv/fonts
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
