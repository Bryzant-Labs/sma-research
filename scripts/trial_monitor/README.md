# Trial Monitor — Daily ClinicalTrials.gov Scraper

Fetches SMA and IDH1 clinical trials from ClinicalTrials.gov daily and syncs them to the research platforms.

## What It Scrapes

| Topic | Condition Query | Platforms |
|-------|----------------|-----------|
| SMA   | `Spinal Muscular Atrophy` | https://sma-research.info |
| IDH1  | `IDH1 mutant OR isocitrate dehydrogenase 1` | https://idh1-research.info |

**Status filters**: RECRUITING, ACTIVE_NOT_RECRUITING, ENROLLING_BY_INVITATION, plus COMPLETED trials updated within the past 90 days.

## Files

| File | Purpose |
|------|---------|
| `trial_scraper.py` | Main script — fetches, diffs, and syncs |
| `payload_builder.py` | Maps CT.gov v2 schema → platform `/api/v2/trials` payload |
| `run_daily.sh` | Shell wrapper for cron |
| `tests/test_scraper.py` | Unit tests (23 cases) |

## Required Environment Variables

```bash
export SMA_PLATFORM_API_KEY="your-sma-api-key"
export IDH1_PLATFORM_API_KEY="your-idh1-api-key"
export SLACK_RESEARCH_WEBHOOK="https://hooks.slack.com/..."  # optional
```

Set in `~/.bashrc` or pass via cron environment.

## Running Manually

```bash
cd ~/sma-research/scripts/trial_monitor
source ~/sma-research/venv/bin/activate

# Full sync
python trial_scraper.py --topic sma --platform https://sma-research.info
python trial_scraper.py --topic idh1 --platform https://idh1-research.info

# Dry run (no platform writes)
python trial_scraper.py --topic sma --platform https://sma-research.info --dry-run
```

## Cron Setup

Add to crontab (`crontab -e`):

```
0 5 * * * /home/bryza/sma-research/scripts/trial_monitor/run_daily.sh >> /home/bryza/sma-research/logs/trial_cron.log 2>&1
```

Logs are written to `~/sma-research/logs/trial_scraper_<topic>_<date>.log`.

## Slack Alerts

Significant changes trigger a Slack DM via `SLACK_RESEARCH_WEBHOOK`:
- New Phase 3 trial discovered
- Results section posted on an existing trial
- Status flip to recruiting / completed / terminated

**HARD RULE**: Only `SLACK_RESEARCH_WEBHOOK` is used. Never posts to Bryzant or Tuvoc channels.

## Adding a New Condition

1. Add an entry to `TOPIC_CONFIG` in `trial_scraper.py`:

```python
TOPIC_CONFIG["myopic"] = {
    "condition": "My Disease OR alternate name",
    "api_key_env": "MYOPIC_PLATFORM_API_KEY",
}
```

2. Add the `--topic myopic` choice to the `argparse` choices list.

3. Add a run line to `run_daily.sh`:

```bash
python trial_scraper.py --topic myopic --platform https://myopic-research.info
```

## Idempotency

Running twice in one day is safe:
- `check_trial_exists` uses `GET /api/v2/trials?nct_id=` before any write
- Trials are skipped if `last_update_posted` date is unchanged
- ClinicalTrials.gov rarely updates a trial twice in 24 hours

## Debugging

```bash
# Check what would be fetched without writing
python trial_scraper.py --topic sma --platform https://sma-research.info --dry-run

# See last log
tail -50 ~/sma-research/logs/trial_scraper_sma_$(date +%Y-%m-%d).log

# Run tests
cd ~/sma-research/scripts/trial_monitor
python -m pytest tests/test_scraper.py -v
```

## Rate Limits

ClinicalTrials.gov allows ~50 requests/min per IP. The scraper sleeps 1.2s between pages and retries with exponential backoff on 429/503. A full SMA scrape (~500 trials) takes roughly 30–60 seconds.
