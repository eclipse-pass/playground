FROM node:16.4.2-alpine3.11

WORKDIR /app
EXPOSE 80/tcp
COPY . /app

RUN \
    cd /app && \
    yarn install

CMD ./node_modules/.bin/ember server --port 80
