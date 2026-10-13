#!/bin/bash

# Restore the v9.8 base castle zip molds from git history into data/0-base-stls.
# data/*/* is gitignored, so these files are not present in a fresh clone.

BASE_STLS_DIR="./data/0-base-stls"
SOURCE_COMMIT="5a38914"

if [ ! -d ".git" ]; then
    echo "Please run this script at the root of the braillest/tooling repo"
    exit 1
fi

mkdir -p "$BASE_STLS_DIR"

for NAME in Positive-Castle-Zip-Mold-v9.8.stl Negative-Castle-Zip-Mold-v9.8.stl; do
    if [ -f "$BASE_STLS_DIR/$NAME" ]; then
        echo "Already exists: $BASE_STLS_DIR/$NAME"
        continue
    fi
    git show "$SOURCE_COMMIT:data/base-stls/$NAME" > "$BASE_STLS_DIR/$NAME" || exit 1
    echo "Restored: $BASE_STLS_DIR/$NAME"
done

exit 0
