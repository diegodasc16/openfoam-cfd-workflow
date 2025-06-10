#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

print_section() {
  echo ""
  echo "============================================================"
  echo "🟢 $1"
  echo "============================================================"
}

print_section "1. Generating STL files with Blender"
"/home/diego/blender-4.1.0-linux-x64/blender" --background --python "$SCRIPTS_DIR/cyl_generation.py"

print_section "2. Generating OpenFOAM case structure"
python3 "$SCRIPTS_DIR/case_structure.py"

print_section "3. Running blockMesh and surfaceFeatureExtract"
python3 "$SCRIPTS_DIR/preprocess_cases.py"

print_section "4. Running snappyHexMesh (parallel or serial)"
python3 "$SCRIPTS_DIR/mesh_cases.py"

print_section "5. Running simulation (parallel or serial)"
python3 "$SCRIPTS_DIR/solve_cases.py"

print_section "✅ Pipeline completed successfully!"

