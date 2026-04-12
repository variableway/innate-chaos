 #!/bin/bash
  # update-submodules.sh — Initialize and update all git submodules

  set -e

  echo "Initializing and updating all submodules..."
  git submodule update --init --recursive

  echo ""
  echo "Submodule status:"
  git submodule status

