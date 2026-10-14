#!/bin/zsh
TASK_PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$TASK_PROJECT_DIR" || exit 1
"$TASK_PROJECT_DIR/.venv/bin/python" "$TASK_PROJECT_DIR/tools/s3_gallery.py" --open
TASK_VIEWER_EXIT=$?
if [ "$TASK_VIEWER_EXIT" -ne 0 ]; then
  echo "The viewer could not start. Read the message above, then press Enter to close."
  read
fi
