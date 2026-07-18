# =============================================================================
# XGIC Payload CMS Development Container
# Optimized for layer caching and fast rebuilds
# =============================================================================

# -----------------------------------------------------------------------------
# Python stage (official slim image, pinned per ADR-0002 / XGIC Python 3.14
# baseline). Must share the same Debian generation as node:lts-slim so the
# multi-stage COPY of /usr/local has a matching glibc (bookworm = 2.36).
# Default python:3.14-slim tracks trixie (glibc 2.38+) and breaks node:lts-slim.
# -----------------------------------------------------------------------------
FROM python:3.14.6-slim-bookworm AS python

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
    && curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
       gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg \
    && echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/debian $(. /etc/os-release && echo $VERSION_CODENAME)/mongodb-org/7.0 main" | \
       tee /etc/apt/sources.list.d/mongodb-org-7.0.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends mongodb-mongosh \
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

# Bring in clean Python installation (multi-stage copy for reproducibility
# and to avoid PPA fragility). Source stage is slim-bookworm so glibc matches
# node:lts-slim (see python stage comment above).
COPY --from=python /usr/local /usr/local

# Ensure the new Python is early in PATH (before any system python3)
ENV PATH="/usr/local/bin:${PATH}"

# Create isolated Python venv (for modular XGIC CLI + template scripts).
# The base image is chosen for glibc compatibility with node:lts-slim.
ENV PYTHON_VENV=/opt/venv
RUN /usr/local/bin/python3 -m venv ${PYTHON_VENV} \
    && ${PYTHON_VENV}/bin/pip install --no-cache-dir \
       --upgrade pip setuptools wheel \
    && rm -rf /root/.cache/pip

# Make venv tools available globally in the container (takes precedence)
ENV PATH="${PYTHON_VENV}/bin:${PATH}"

# Default Docker Compose identity for this template (product-agnostic xgic CLI flags/env).
ENV XGIC_COMPOSE_FILE=.devcontainer/docker-compose.yml \
    XGIC_COMPOSE_PROJECT=xgic-payload-cms-dev-containers \
    XGIC_PRIMARY_SERVICE=xgic-payload-cms-dev-containers

# Allow the app user (node) to install additional packages into the venv
# when needed. Venv is created as root but the remoteUser is node.
RUN chown -R ${APP_USER}:${APP_USER} ${PYTHON_VENV}

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

# Install modular XGIC CLI from PyPI (standard consumer path).
# See https://github.com/xgic/ai/blob/main/docs/python-package-release.md
# Template is a consumer only — no in-tree CLI package (ADR-0005 B5 cutover).
# Use uv for install (XGIC standard toolchain).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN uv pip install --python ${PYTHON_VENV}/bin/python --no-cache \
        "xgic-cli>=0.2.0,<0.3" \
        "xgic-dev-cli>=0.2.0,<0.3" \
        "xgic-payload-cms-cli>=0.2.0,<0.3" \
    && uv pip install --python ${PYTHON_VENV}/bin/python --no-cache \
        -e . \
    && rm -rf /root/.cache/uv /root/.cache/pip

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
