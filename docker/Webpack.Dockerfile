FROM node:8.5-alpine
LABEL maintainer="Dotkom <dotkom@online.ntnu.no>"

ENV APP_DIR=/srv/app

WORKDIR $APP_DIR

COPY package.json $APP_DIR/package.json
RUN yarn

CMD ["bash"]
