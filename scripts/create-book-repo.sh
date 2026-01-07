#!/bin/bash

# Initialize variables.
CONTAINER_NAME="braillest_tooling"
REPO_NAME="braillest/tooling"
COVER_ART_SOURCE_FILE="//html/cover-art.html"
BASE_STLS_DIR="./data/0-base-stls"
TEXTS_DIR="./data/1-texts"
BRAILLE_DIR="./data/2-braille"
BACK_TRANSLATIONS_DIR="./data/3-back-translations"
FORMATTED_BRAILLE_DIR="./data/4-formatted-braille"
PAGINATED_BRAILLE_DIR="./data/5-paginated-braille"
BRAILLE_MOLDS_DIR="./data/6-braille-molds"
BRAILLEST_BOOKS_DIR="./braillest-books"

BOOK_NAME=""
TEXTS_BOOK_FILE=""
BRAILLE_BOOK_FILE=""
BACK_TRANSLATIONS_BOOK_FILE=""
FORMATTED_BRAILLE_BOOK_FILE=""
PAGINATED_BRAILLE_BOOK_DIR=""
BRAILLE_MOLDS_BOOK_DIR=""
BRAILLEST_BOOKS_BOOK_DIR=""

BRAILLEST_BOOKS_BOOK_BASE_STLS_DIR=""
BRAILLEST_BOOKS_BOOK_TEXTS_DIR=""
BRAILLEST_BOOKS_BOOK_BRAILLE_DIR=""
BRAILLEST_BOOKS_BOOK_BACK_TRANSLATIONS_DIR=""
BRAILLEST_BOOKS_BOOK_FORMATTED_BRAILLE_DIR=""
BRAILLEST_BOOKS_BOOK_PAGINATED_BRAILLE_DIR=""
BRAILLEST_BOOKS_BOOK_BRAILLE_MOLDS_DIR=""

# Validate that docker is running.
docker ps > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Docker is not running"
    exit 1
fi

# Validate that the container is running.
docker ps | grep "$CONTAINER_NAME" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Container is not running"
    echo "Expected container name: $CONTAINER_NAME"
    echo "Please run 'docker-compose up -d' to start the container"
    exit 1
fi

# Validate base stls directory exists.
if [ ! -d "$BASE_STLS_DIR" ]; then
    echo "Base stls directory does not exist"
    echo "Expected directory: $BASE_STLS_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate texts directory exists.
if [ ! -d "$TEXTS_DIR" ]; then
    echo "Texts directory does not exist"
    echo "Expected directory: $TEXTS_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate braille directory exists.
if [ ! -d "$BRAILLE_DIR" ]; then
    echo "Braille directory does not exist"
    echo "Expected directory: $BRAILLE_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate back translations directory exists.
if [ ! -d "$BACK_TRANSLATIONS_DIR" ]; then
    echo "Back translations directory does not exist"
    echo "Expected directory: $BACK_TRANSLATIONS_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate formatted braille directory exists.
if [ ! -d "$FORMATTED_BRAILLE_DIR" ]; then
    echo "Formatted braille directory does not exist"
    echo "Expected directory: $FORMATTED_BRAILLE_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate paginated braille directory exists.
if [ ! -d "$PAGINATED_BRAILLE_DIR" ]; then
    echo "Paginated braille directory does not exist"
    echo "Expected directory: $PAGINATED_BRAILLE_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate braille molds directory exists.
if [ ! -d "$BRAILLE_MOLDS_DIR" ]; then
    echo "Braille molds directory does not exist"
    echo "Expected directory: $BRAILLE_MOLDS_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/etooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate braillest-books directory exists.
if [ ! -d "$BRAILLEST_BOOKS_DIR" ]; then
    echo "Braillest-books directory does not exist"
    echo "Expected path: $BRAILLEST_BOOKS_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Check if git is installed.
if ! command -v git &> /dev/null; then
    echo "Git is not installed"
    exit 1
fi

# Check if git is initialized.
if [ ! -d ".git" ]; then
    echo "Git is not initialized"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Check script argument for book name.
if [ -z "$1" ]; then
    echo "Book name cannot be empty"
    exit 1
fi

BOOK_NAME=$1

# Populate book path variables.
TEXTS_BOOK_FILE="$TEXTS_DIR/$BOOK_NAME.txt"
BRAILLE_BOOK_FILE="$BRAILLE_DIR/$BOOK_NAME.txt"
BACK_TRANSLATIONS_BOOK_FILE="$BACK_TRANSLATIONS_DIR/$BOOK_NAME.txt"
FORMATTED_BRAILLE_BOOK_FILE="$FORMATTED_BRAILLE_DIR/$BOOK_NAME.txt"
PAGINATED_BRAILLE_BOOK_DIR="$PAGINATED_BRAILLE_DIR/$BOOK_NAME"
BRAILLE_MOLDS_BOOK_DIR="$BRAILLE_MOLDS_DIR/$BOOK_NAME"

# Replace spaces with dashes.
BRAILLEST_BOOKS_BOOK_DIR="$BRAILLEST_BOOKS_DIR/$(echo "$BOOK_NAME" | tr ' ' '-')"

# Validate texts book file exists.
if [ ! -f "$TEXTS_BOOK_FILE" ]; then
    echo "Texts book file does not exist"
    echo "Expected path: $TEXTS_BOOK_FILE"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate braille book file exists.
if [ ! -f "$BRAILLE_BOOK_FILE" ]; then
    echo "Braille book file does not exist"
    echo "Expected path: $BRAILLE_BOOK_FILE"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate back translations book file exists.
if [ ! -f "$BACK_TRANSLATIONS_BOOK_FILE" ]; then
    echo "Back translations book file does not exist"
    echo "Expected path: $BACK_TRANSLATIONS_BOOK_FILE"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate formatted braille book file exists.
if [ ! -f "$FORMATTED_BRAILLE_BOOK_FILE" ]; then
    echo "Formatted braille book file does not exist"
    echo "Expected path: $FORMATTED_BRAILLE_BOOK_FILE"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate paginated braille book directory exists.
if [ ! -d "$PAGINATED_BRAILLE_BOOK_DIR" ]; then
    echo "Paginated braille book directory does not exist"
    echo "Expected path: $PAGINATED_BRAILLE_BOOK_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate paginated braille book directory is not empty.
if [ -z "$(ls -A "$PAGINATED_BRAILLE_BOOK_DIR" 2>/dev/null)" ]; then
    echo "Paginated braille book directory is empty"
    echo "Expected path: $PAGINATED_BRAILLE_BOOK_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate braille molds book directory exists.
if [ ! -d "$BRAILLE_MOLDS_BOOK_DIR" ]; then
    echo "Braille molds book directory does not exist"
    echo "Expected path: $BRAILLE_MOLDS_BOOK_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Validate braille molds book directory is not empty.
if [ -z "$(ls -A "$BRAILLE_MOLDS_BOOK_DIR" 2>/dev/null)" ]; then
    echo "Braille molds book directory is empty"
    echo "Expected path: $BRAILLE_MOLDS_BOOK_DIR"
    echo "Current directory: $(pwd)"
    echo "Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book"
    exit 1
fi

# Create braillest-books book directory if it does not exist.
if [ ! -d "$BRAILLEST_BOOKS_BOOK_DIR" ]; then
    mkdir -p "$BRAILLEST_BOOKS_BOOK_DIR"
fi

# Divide BOOK_NAME into TITLE and AUTHOR making sure to handle the edge case where "by" might be used in the title.
TITLE=${BOOK_NAME% by *}
AUTHOR=${BOOK_NAME##* by }
COVER_ART_OUTPUT_FILE="//braillest-books/$(echo "$BOOK_NAME" | tr ' ' '-')/cover-art.jpg"
SELECTOR="#book-title"

# Create query string.
QUERY_STRING="title=$(echo "$TITLE" | sed 's/ /%20/g')&author=$(echo "$AUTHOR" | sed 's/ /%20/g')"

# Call docker container to create cover art image with TITLE and AUTHOR.
docker exec "$CONTAINER_NAME" python generate_cover_art.py "$COVER_ART_SOURCE_FILE" "$QUERY_STRING" "$SELECTOR" "$COVER_ART_OUTPUT_FILE"

BRAILLEST_BOOKS_BOOK_BASE_STLS_DIR="$BRAILLEST_BOOKS_BOOK_DIR/0-base-stls"
BRAILLEST_BOOKS_BOOK_TEXTS_DIR="$BRAILLEST_BOOKS_BOOK_DIR/1-texts"
BRAILLEST_BOOKS_BOOK_BRAILLE_DIR="$BRAILLEST_BOOKS_BOOK_DIR/2-braille"
BRAILLEST_BOOKS_BOOK_BACK_TRANSLATIONS_DIR="$BRAILLEST_BOOKS_BOOK_DIR/3-back-translations"
BRAILLEST_BOOKS_BOOK_FORMATTED_BRAILLE_DIR="$BRAILLEST_BOOKS_BOOK_DIR/4-formatted-braille"
BRAILLEST_BOOKS_BOOK_PAGINATED_BRAILLE_DIR="$BRAILLEST_BOOKS_BOOK_DIR/5-paginated-braille"
BRAILLEST_BOOKS_BOOK_BRAILLE_MOLDS_DIR="$BRAILLEST_BOOKS_BOOK_DIR/6-braille-molds"
BRAILLEST_BOOKS_BOOK_MANIFEST_FILE="$BRAILLEST_BOOKS_BOOK_DIR/manifest.yml"

# Create braillest-books book base stls directory if it does not exist.
if [ ! -d "$BRAILLEST_BOOKS_BOOK_BASE_STLS_DIR" ]; then
    mkdir -p "$BRAILLEST_BOOKS_BOOK_BASE_STLS_DIR"
fi

# Create braillest-books book texts directory if it does not exist.
if [ ! -d "$BRAILLEST_BOOKS_BOOK_TEXTS_DIR" ]; then
    mkdir -p "$BRAILLEST_BOOKS_BOOK_TEXTS_DIR"
fi

# Create braillest-books book braille directory if it does not exist.
if [ ! -d "$BRAILLEST_BOOKS_BOOK_BRAILLE_DIR" ]; then
    mkdir -p "$BRAILLEST_BOOKS_BOOK_BRAILLE_DIR"
fi

# Create braillest-books book back translations directory if it does not exist.
if [ ! -d "$BRAILLEST_BOOKS_BOOK_BACK_TRANSLATIONS_DIR" ]; then
    mkdir -p "$BRAILLEST_BOOKS_BOOK_BACK_TRANSLATIONS_DIR"
fi

# Create braillest-books book formatted braille directory if it does not exist.
if [ ! -d "$BRAILLEST_BOOKS_BOOK_FORMATTED_BRAILLE_DIR" ]; then
    mkdir -p "$BRAILLEST_BOOKS_BOOK_FORMATTED_BRAILLE_DIR"
fi

# Create braillest-books book paginated braille directory if it does not exist.
if [ ! -d "$BRAILLEST_BOOKS_BOOK_PAGINATED_BRAILLE_DIR" ]; then
    mkdir -p "$BRAILLEST_BOOKS_BOOK_PAGINATED_BRAILLE_DIR"
fi

# Create braillest-books book braille molds directory if it does not exist.
if [ ! -d "$BRAILLEST_BOOKS_BOOK_BRAILLE_MOLDS_DIR" ]; then
    mkdir -p "$BRAILLEST_BOOKS_BOOK_BRAILLE_MOLDS_DIR"
fi

# Copy the contents of the base stls directory into the braillest-books book base stls directory if newer.
cp -ur "$BASE_STLS_DIR/." "$BRAILLEST_BOOKS_BOOK_BASE_STLS_DIR"

# Remove .gitkeep file from base stls directory.
rm "$BRAILLEST_BOOKS_BOOK_BASE_STLS_DIR/.gitkeep"

# Copy texts file into braillest-books book texts directory if newer.
cp -u "$TEXTS_BOOK_FILE" "$BRAILLEST_BOOKS_BOOK_TEXTS_DIR"

# Copy braille file into braillest-books book braille directory if newer.
cp -u "$BRAILLE_BOOK_FILE" "$BRAILLEST_BOOKS_BOOK_BRAILLE_DIR"

# Copy back translations file into braillest-books book back translations directory if newer.
cp -u "$BACK_TRANSLATIONS_BOOK_FILE" "$BRAILLEST_BOOKS_BOOK_BACK_TRANSLATIONS_DIR"

# Copy formatted braille file into braillest-books book formatted braille directory if newer.
cp -u "$FORMATTED_BRAILLE_BOOK_FILE" "$BRAILLEST_BOOKS_BOOK_FORMATTED_BRAILLE_DIR"

# Copy the contents of the paginated braille directory into the braillest-books book paginated braille directory if newer.
cp -ur "$PAGINATED_BRAILLE_BOOK_DIR/." "$BRAILLEST_BOOKS_BOOK_PAGINATED_BRAILLE_DIR"

# Copy the contents of the braille molds directory into the braillest-books book braille molds directory if newer.
cp -ur "$BRAILLE_MOLDS_BOOK_DIR/." "$BRAILLEST_BOOKS_BOOK_BRAILLE_MOLDS_DIR"

# Get braillest/tooling repo's current commit hash.
COMMIT_HASH=$(git rev-parse HEAD)

# Get current user.
USER=$(git config user.name)

# Create manifest yml file using book name, commit hash, and user.
echo "book: $BOOK_NAME" > "$BRAILLEST_BOOKS_BOOK_MANIFEST_FILE"
echo "repo: $REPO_NAME" >> "$BRAILLEST_BOOKS_BOOK_MANIFEST_FILE"
echo "commit: $COMMIT_HASH" >> "$BRAILLEST_BOOKS_BOOK_MANIFEST_FILE"
echo "user: $USER" >> "$BRAILLEST_BOOKS_BOOK_MANIFEST_FILE"

# Create README.md file.
echo "![Cover Art](cover-art.jpg)" > "$BRAILLEST_BOOKS_BOOK_DIR/README.md"

# Create .gitignore file to ignore .zip files.
echo "*.zip" > "$BRAILLEST_BOOKS_BOOK_DIR/.gitignore"

# Call tooling container to zip molds.
docker exec "$CONTAINER_NAME" python zip_molds.py "//$BRAILLEST_BOOKS_BOOK_BRAILLE_MOLDS_DIR" "//$BRAILLEST_BOOKS_BOOK_DIR"

# Initialize git repository in braillest-books book directory.
git init "$BRAILLEST_BOOKS_BOOK_DIR"

# Change to the braillest-books book directory.
cd "$BRAILLEST_BOOKS_BOOK_DIR"

# Log message to the user that this will take a while.
echo "Adding files to git repository. This will take a while..."

# Add all files to the newly created child git repository.
git add .

# Log message to the user that this will take a while.
echo "Committing files to git repository. This will take a while..."

# Commit all files to the newly created child git repository.
git commit -m "automated initial commit"

# Add expected git remote
git remote add origin "git@github.com:Braillest-Books/$(echo "$BOOK_NAME" | tr ' ' '-').git"

# Log success message.
echo ""
echo "Successfully created book repository: $BRAILLEST_BOOKS_BOOK_DIR"

# Tell user to create the remote repository on GitHub.
echo ""
echo "Please create the repository on GitHub:"
echo "$(echo "$BOOK_NAME" | tr ' ' '-')"
echo ""
echo "Then run the following command to push to the remote repository:"
echo "git push origin master"

exit 0
