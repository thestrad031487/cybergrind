#!/bin/bash

# Ensure ollama is running and ready
if ! curl -s http://127.0.0.1:11434 > /dev/null 2>&1; then
    echo "Starting Ollama..."
    /usr/local/bin/ollama serve &
    # Wait until Ollama is actually ready (up to 60 seconds)
    for i in $(seq 1 30); do
        sleep 2
        if curl -s http://127.0.0.1:11434 > /dev/null 2>&1; then
            echo "Ollama ready after $((i * 2))s"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "Ollama failed to start after 60s, aborting"
osascript -e 'tell app "System Events" to display dialog "CyberGrind: Ollama failed to start — no post generated" buttons {"OK"} default button 1'            exit 1
        fi
    done
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
osascript -e 'tell app "System Events" to display dialog "CyberGrind: Daily cybernews posted successfully" buttons {"OK"} default button 1'    echo "Post published successfully"
else
osascript -e 'tell app "System Events" to display dialog "CyberGrind: No new post — already up to date" buttons {"OK"} default button 1'    echo "No new post to publish"
fi