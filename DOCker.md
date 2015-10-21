# If you run docker on mac os x, get the IP address to the virtualbox middleware, which is the one you need to connect to to view the webpage.
# Other OS can utilize localhost:<port> or whatever is available.

- `docker build -t onlineweb4 .`  build from scratch
- `docker-compose up -d`  run ow4 (runserver) (-d = detached)

- `docker run web python manage.py <django cmd>`  # run django commands from host, e.g. `migrate`
