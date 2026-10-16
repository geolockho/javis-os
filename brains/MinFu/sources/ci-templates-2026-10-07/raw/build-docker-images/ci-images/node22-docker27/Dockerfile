FROM docker:27.5.1-cli AS docker-cli

FROM node:22-alpine

COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker-cli /usr/local/libexec/docker/cli-plugins/docker-buildx \
  /usr/local/libexec/docker/cli-plugins/docker-buildx

RUN apk add --no-cache git \
  && docker --version \
  && docker buildx version \
  && git --version
