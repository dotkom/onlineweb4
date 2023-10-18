FROM gitpod/workspace-full

RUN pyenv install 3.11.5

RUN pyenv global 3.11.5

RUN pip install poetry

RUN poetry config virtualenvs.in-project true

ENV WEBPACK_DEV_GITPOD=true
ENV WEBPACK_DEV_HTTPS=true
