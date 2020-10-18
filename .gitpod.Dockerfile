FROM gitpod/workspace-full

RUN pyenv install 3.7.9

RUN pyenv global 3.7.9

ENV WEBPACK_DEV_GITPOD=true
ENV WEBPACK_DEV_HTTPS=true