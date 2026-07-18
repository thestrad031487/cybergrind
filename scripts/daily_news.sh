#!/bin/bash
set -uo pipefail

LOG_PREFIX="[daily_news $(date '+%Y-%m-%d %H:%M:%S')]"
CYBERGRIND_DIR="$HOME/cybergrind"
OLLAMA_URL="http://localhost:11434"
PIPER_VOICE="/opt/piper-voices/en_US-lessac-medium.onnx"

log() {
    echo "$LOG_PREFIX $1"
}

# --- Confirm Ollama is reachable (it runs persistently in ai-stack, we don't start it here) ---
if ! curl -s "$OLLAMA_URL" > /dev/null 2>&1; then
    log "ERROR: Ollama not reachable at $OLLAMA_URL — aborting, no post generated."
    # Optional: uncomment and fill in to alert via the existing ai-stack Slack bot
    # curl -s -X POST -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
    #   -H "Content-Type: application/json" \
    #   -d '{"channel":"#serverhealth","text":"CyberGrind: Ollama unreachable, daily_news.sh aborted"}' \
    #   https://slack.com/api/chat.postMessage
    exit 1
fi
log "Ollama reachable."

cd "$CYBERGRIND_DIR" || { log "ERROR: cannot cd to $CYBERGRIND_DIR"; exit 1; }

set -a
source "$CYBERGRIND_DIR/.env"
set +a

# --- Pull latest before doing anything, rebase not merge ---
if ! git pull --rebase origin main; then
    log "ERROR: git pull --rebase failed — likely a conflict needing manual resolution. Aborting."
    exit 1
fi

# --- Generate the CyberNews post ---
TODAY=$(date +%Y-%m-%d)
python3 scripts/generate_news.py
if [[ ! -f "content/blog/${TODAY}-cybernews.md" ]]; then
    log "No new CyberNews post generated today — nothing further to do."
    exit 0
fi
log "Generated content/blog/${TODAY}-cybernews.md"

# --- Generate the CISO Brief companion post ---
if python3 scripts/generate_ciso_brief.py --date "$TODAY" --blog-dir content/blog --ollama-model llama3.2:3b; then
    log "Generated content/blog/${TODAY}-ciso-brief.md"
else
    log "WARNING: CISO brief generation failed — continuing without it."
fi

# --- Generate audio for both posts (skips quietly if Piper isn't installed yet) ---
if [ -x "/opt/piper-venv/bin/piper" ] && [[ -f "$PIPER_VOICE" ]]; then
    for slug in "${TODAY}-cybernews" "${TODAY}-ciso-brief"; do
        if [[ -f "content/blog/${slug}.md" ]]; then
            python3 scripts/generate_audio.py \
                --post "content/blog/${slug}.md" \
                --static-dir static/audio \
                --voice-model "$PIPER_VOICE" \
                && log "Generated audio for ${slug}" \
                || log "WARNING: audio generation failed for ${slug}"
        fi
    done
else
    log "Piper not installed yet — skipping audio generation (Phase 4 pending)."
fi

# --- Commit and push, with one retry on rejection ---
if [[ -n $(git status --porcelain content/blog/ static/audio/ 2>/dev/null) ]]; then
    git add content/blog/ static/audio/ 2>/dev/null
    git commit -m "auto: daily cybernews ${TODAY}"

    if git push origin main; then
        log "Post published successfully."
    else
        log "Push rejected, retrying after rebase..."
        if git pull --rebase origin main && git push origin main; then
            log "Post published successfully on retry."
        else
            log "ERROR: push failed after retry — needs manual resolution."
            exit 1
        fi
    fi
else
    log "No new content to publish."
fi
