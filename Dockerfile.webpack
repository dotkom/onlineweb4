FROM node:8.5-alpine
LABEL maintainer="dotkom <dotkom@online.ntnu.no>"

ENV APP_DIR=/srv/app

RUN mkdir -p $APP_DIR
WORKDIR $APP_DIR

COPY package.json $APP_DIR/package.json
RUN yarn

CMD ["bash"]
