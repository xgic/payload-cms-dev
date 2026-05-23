FROM node:lts-slim AS core
LABEL net.xgic.maintainer="XGIC"
LABEL net.xgic.version="0.1.0"
LABEL net.xgic.description="XGIC Payload CMS Development Container"
LABEL net.xgic.stage="Core"

ENV APP_USER=node
ENV APP_HOME_DIR=/home/${APP_USER}
ENV APP_BIN_DIR=${APP_HOME_DIR}/.local/bin
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8
ENV WORKSPACE=/app
ENV XG_AIS_HOST_TYPE=xgic-devcontainer

FROM core AS dev_tools
LABEL net.xgic.stage="Development Tools"

# Install system deps + pnpm
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    gnupg \
    iproute2 \
    iputils-ping \
    iputils-tracepath \
    jq \
    locales \
    lsb-release \
    rsync \
    ssh \
    unzip \
    wget \
    zlib1g-dev \
    # Install Docker CLI and Buildx plugin (for local container builds)
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg -o \
    /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && echo "deb [arch=$(dpkg --print-architecture) \
    signed-by=/etc/apt/keyrings/docker.asc] \
    https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update --yes --quiet && apt-get install --yes --quiet \
    --no-install-recommends \
    docker-buildx-plugin \
    docker-ce-cli \
    docker-compose-plugin \
    # Best-practice PostgreSQL 18 client installation (matches server)
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
    gpg --dearmor -o /usr/share/keyrings/postgresql-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/postgresql-archive-keyring.gpg] \
    https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
    | tee /etc/apt/sources.list.d/pgdg.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client-18 \
    # Generate en_US.UTF-8 locale (eliminates perl/psql warnings)
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias \
    en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get upgrade --yes --quiet \
    && rm -rf /var/lib/apt/lists/* \
    # Install pnpm via corepack
    && corepack enable \
    && corepack use pnpm@10

# Setup app user and groups
RUN chsh -s /bin/bash ${APP_USER} \
    && groupadd -g 994 docker \
    && usermod -aG docker ${APP_USER} \
    && groupadd -g 2001 ${APP_USER}-${APP_ENV} \
    && usermod -aG docker,sudo,${APP_USER}-${APP_ENV} ${APP_USER} \
    && mkdir -p ${APP_HOME_DIR}/.vscode-server/extensions \
    && chown -R ${APP_USER}:${APP_USER} ${APP_HOME_DIR}/.vscode-server

FROM dev_tools AS dev
LABEL net.xgic.stage="Development"
ENV APP_ENV=dev

# Copy code
COPY --chown=${APP_USER}:${APP_USER} . .

# Install dependencies
USER ${APP_USER}
# RUN pnpm install --force

FROM core AS prod
LABEL net.xgic.stage="Production"
ENV APP_ENV=prod

# Copy code
COPY --chown=${APP_USER}:${APP_USER} . .

# Install dependencies
USER ${APP_USER}
# RUN pnpm install --prod

# Set default command.
CMD ["tail", "-f", "/dev/null"]
