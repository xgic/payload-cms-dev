# =============================================================================
# XGIC Payload CMS Development Container
# Optimized for layer caching and fast rebuilds
# =============================================================================

# -----------------------------------------------------------------------------
# Python 3.14 stage (clean, future-proof installation via official image)
# -----------------------------------------------------------------------------
FROM python:3.14-slim AS python

# -----------------------------------------------------------------------------
# Stage 1: Core base (changes very rarely)
# -----------------------------------------------------------------------------
FROM node:lts-slim AS core

LABEL net.xgic.maintainer="XGIC"
LABEL net.xgic.description="XGIC Payload CMS Development Container"

ENV APP_USER=node
ENV APP_HOME_DIR=/home/${APP_USER}
ENV APP_BIN_DIR=${APP_HOME_DIR}/.local/bin
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8
ENV WORKSPACE=/workspace
ENV XG_AIS_HOST_TYPE=xgic-devcontainer

# Default environment (overridden in dev/prod stages)
ENV APP_ENV=dev

# -----------------------------------------------------------------------------
# Stage 2: System dependencies (changes infrequently)
# This is the heaviest layer. Keep it stable.
# -----------------------------------------------------------------------------
FROM core AS system-base

# Install all system packages in one layer for better apt caching
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
        build-essential \
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
        shellcheck \
        ssh \
        unzip \
        wget \
        zlib1g-dev \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL \
       https://download.docker.com/linux/debian/gpg \
       -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && printf '%s\n' \
       "deb [arch=$(dpkg --print-architecture) \
signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/debian \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
       | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update --yes --quiet \
    && apt-get install --yes --quiet --no-install-recommends \
        docker-buildx-plugin \
        docker-ce-cli \
        docker-compose-plugin \
    && curl -fsSL \
       https://www.postgresql.org/media/keys/ACCC4CF8.asc \
       | gpg --dearmor -o \
         /usr/share/keyrings/postgresql-archive-keyring.gpg \
    && printf '%s\n' \
       "deb [signed-by=/usr/share/keyrings/\
postgresql-archive-keyring.gpg] \
https://apt.postgresql.org/pub/repos/apt \
$(lsb_release -cs)-pgdg main" \
       | tee /etc/apt/sources.list.d/pgdg.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       postgresql-client-18 \
    && localedef -i en_US -c -f UTF-8 \
       -A /usr/share/locale/locale.alias en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Stage 3: User and directory setup (changes rarely)
# -----------------------------------------------------------------------------
FROM system-base AS user-setup

RUN chsh -s /bin/bash ${APP_USER} \
    && groupadd -g 994 docker \
    && usermod -aG docker ${APP_USER} \
    && groupadd -g 2001 ${APP_USER}-${APP_ENV} \
    && usermod -aG docker,sudo,${APP_USER}-${APP_ENV} ${APP_USER} \
    && mkdir -p ${APP_HOME_DIR}/.vscode-server/extensions \
    && mkdir -p ${WORKSPACE} \
    && chown -R ${APP_USER}:${APP_USER} \
       ${APP_HOME_DIR}/.vscode-server ${WORKSPACE}

# -----------------------------------------------------------------------------
# Stage 4: Development tools (pnpm, Python venv) - changes occasionally
# -----------------------------------------------------------------------------
FROM user-setup AS dev-tools

# Enable pnpm via corepack
RUN corepack enable && corepack use pnpm@10

# Bring in clean Python 3.14 installation (multi-stage copy for reproducibility
# and to avoid PPA fragility). This is the recommended future-proof approach
# when the primary runtime is Node but you need a modern Python for tooling.
COPY --from=python /usr/local /usr/local

# Ensure the new Python is early in PATH (before any system python3)
ENV PATH="/usr/local/bin:${PATH}"

# Create isolated Python 3.14 venv (for devcontainer scripting,
# xde CLI, and testing)
ENV PYTHON_VENV=/opt/venv
RUN /usr/local/bin/python3.14 -m venv ${PYTHON_VENV} \
    && ${PYTHON_VENV}/bin/pip install --no-cache-dir \
       --upgrade pip setuptools wheel \
    && rm -rf /root/.cache/pip

# Make venv tools available globally in the container (takes precedence)
ENV PATH="${PYTHON_VENV}/bin:${PATH}"

# -----------------------------------------------------------------------------
# Stage 5: Development image (frequently changing)
# -----------------------------------------------------------------------------
FROM dev-tools AS dev

LABEL net.xgic.stage="Development"
WORKDIR ${WORKSPACE}

# Note: Test tooling (pytest etc.) is installed on-demand
# from requirements-dev.txt (see TESTING.md).
# See TESTING.md for details.

# Copy source code as late as possible
COPY --chown=${APP_USER}:${APP_USER} . .

USER ${APP_USER}

# Default command for dev container
CMD ["tail", "-f", "/dev/null"]

# -----------------------------------------------------------------------------
# Stage 6: Production / minimal image
# -----------------------------------------------------------------------------
FROM core AS prod

LABEL net.xgic.stage="Production"
WORKDIR ${WORKSPACE}

# Only copy what is strictly necessary for production use of the container
COPY --chown=${APP_USER}:${APP_USER} . .

USER ${APP_USER}

CMD ["tail", "-f", "/dev/null"]
