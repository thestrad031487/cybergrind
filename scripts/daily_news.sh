#!/bin/bash

# Ensure ollama is running
if ! curl -s http://127.0.0.1:11434 > /dev/null 2>&1; then
    /usr/local/bin/ollama serve &
    sleep 10
fi

cd ~/cybergrind

# Pull latest first
git pull

# Run the news generator
python3 scripts/generate_news.py

# If a new file was created, commit and push
if [[ -n $(git status --porcelain content/blog/) ]]; then
    git add content/blog/
    git commit -m "auto: daily cybernews $(date +%Y-%m-%d)"
    git push
    echo "Post published successfully"
else
    echo "No new post to publish"
fi
