#!/bin/bash

# === SETUP SECTION ===
# This section defines the base paths used in the script.

# Get the absolute path to the directory where this script is located.
# This makes the script robust, so it can be run from any location.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define the folder that contains the generated simulation cases.
CASES_DIR="$SCRIPT_DIR/cases"

# Define the folder that contains the STL geometry files (name of the folder is set in the cyl_generation.py).
OUTPUT_DIR="$SCRIPT_DIR/scripts/output"

# === FUNCTION DEFINITION ===
# This function removes a directory only if it exists and prints a message.

remove_if_exists() {
  local path="$1"  # Full path to the directory to remove
  local name="$2"  # Friendly name to display to the user

# Check if directory exists
  if [ -d "$path" ]; then
    rm -rf "$path" # Delete the folder and all its contents
    echo "🗑️  Deleted: $name"
  else
    echo "ℹ️  Not found: $name"
  fi
}

# === USER WARNING ===
# Tell the user which folders will be deleted and ask for confirmation.

echo "🚨 This will permanently delete the following folders:"
echo "- $CASES_DIR"
echo "- $OUTPUT_DIR"

# Ask the user to confirm (default is No)
read -p "Are you sure? [y/N]: " confirm

# === CONDITIONAL EXECUTION ===
# Only proceed if the user typed "y" or "Y"

if [[ "$confirm" =~ ^[Yy]$ ]]; then
  remove_if_exists "$CASES_DIR" "cases/" # Remove the cases folder
  remove_if_exists "$OUTPUT_DIR" "scripts/output/" # Remove the output folder
  echo "✅ Cleanup complete."
else
  echo "❌ Aborted by user." # Do nothing if the user says no
fi

