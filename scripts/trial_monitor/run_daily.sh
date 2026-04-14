#!/bin/bash
# run_daily.sh — Cron wrapper for trial_scraper.py
#
# Crontab entry (install manually):
# 0 5 * * * /home/bryza/sma-research/scripts/trial_monitor/run_daily.sh >> /home/bryza/sma-research/logs/trial_cron.log 2>&1
#
# Required environment variables (set in ~/.bashrc or passed via cron env):
#   SMA_PLATFORM_API_KEY
#   IDH1_PLATFORM_API_KEY
#   SLACK_RESEARCH_WEBHOOK   (optional — omit to disable Slack alerts)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
VENV="${REPO_ROOT}/venv"
LOG_DIR="${REPO_ROOT}/logs"

echo "[$(date -Iseconds)] run_daily.sh starting"

# Activate venv
if [ -f "${VENV}/bin/activate" ]; then
    source "${VENV}/bin/activate"
    echo "[$(date -Iseconds)] venv activated: ${VENV}"
else
    echo "[$(date -Iseconds)] WARNING: venv not found at ${VENV} — using system Python"
fi

cd "${SCRIPT_DIR}"

echo "[$(date -Iseconds)] --- SMA ---"
python trial_scraper.py \
    --topic sma \
    --platform https://sma-research.info \
    --log-dir "${LOG_DIR}"

echo "[$(date -Iseconds)] --- IDH1 ---"
python trial_scraper.py \
    --topic idh1 \
    --platform https://idh1-research.info \
    --log-dir "${LOG_DIR}"

echo "[$(date -Iseconds)] run_daily.sh complete"
