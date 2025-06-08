#!/bin/bash

SMART_FOLDERS_DIR="$HOME/.smart_folders"
SMART_FOLDER_CONFIGS="$SMART_FOLDERS_DIR/configs"

update_smart_folder() {
    local name="$1"
    local config_file="$SMART_FOLDER_CONFIGS/$name.conf"
    local target_dir="$SMART_FOLDERS_DIR/$name"

    source "$config_file"

    mkdir -p "$target_dir"
    rm -f "$target_dir"/*

    # Properly evaluate find with pattern
    while IFS= read -r -d '' file; do
        ln -sf "$file" "$target_dir/"
    done < <(find "$SEARCH_DIR" -type f $(eval echo "$FIND_PATTERN") -print0)
}

create_smart_folder() {
    local name="$1"
    local search_dir="$2"
    local pattern="$3"
    local target_dir="$SMART_FOLDERS_DIR/$name"

    mkdir -p "$target_dir"
    echo "SEARCH_DIR=\"$search_dir\"" > "$SMART_FOLDER_CONFIGS/$name.conf"
    echo "FIND_PATTERN='$pattern'" >> "$SMART_FOLDER_CONFIGS/$name.conf"

    mkdir -p "$target_dir"
    printf 'SEARCH_DIR="%s"\nFIND_PATTERN=%s\n' "$search_dir" "$pattern" > "$SMART_FOLDER_CONFIGS/$name.conf"

    update_smart_folder "$name"
}

case "$1" in
    "create") create_smart_folder "$2" "$3" "$4" ;;
    "update")
        if [ -n "$2" ]; then
            update_smart_folder "$2"
        else
            for conf in "$SMART_FOLDER_CONFIGS"/*.conf; do
                [ -f "$conf" ] || continue
                update_smart_folder "$(basename "$conf" .conf)"
            done
        fi
        ;;
    *) echo "Usage: $0 create <name> <search_dir> <pattern>" ;;
esac
