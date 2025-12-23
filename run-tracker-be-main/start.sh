#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

uv run alembic upgrade head
uv run python -m app.main