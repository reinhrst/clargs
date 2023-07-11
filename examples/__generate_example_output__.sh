#!/bin/bash

CMDLINE='^>>> python [^ ]+\.py ([^)#]*)(#.*)?\(returncode: ([0-9]+)\)$'
TMPDIR=$(mktemp -d)


function processfile() {
    FILENAME="$1"
    TARGETFILE="$TMPDIR/$(basename "$FILENAME")"
    LINES=($(grep -n '^"""' "$FILENAME" | cut -f1 -d:))
    if [[ ${LINES[0]} != "1" ]]; then
        echo "Skipping $FILENAME; no commands found"
        return 0;
    fi
    echo "Target: $TARGETFILE"

    TOPDOC="$(cat "$FILENAME" | head -n $(( LINES[1] - 1 )) | tail -n $(( LINES[1] - 2)))"
    COMMANDLINES="$(echo "$TOPDOC" | grep -E "$CMDLINE")"

    echo '"""' >> "$TARGETFILE"
    echo 'Examples:' >> "$TARGETFILE"
    echo >> "$TARGETFILE"
    echo "$COMMANDLINES" | while read -r line; do
        ARGUMENTS="$(echo ${line} | sed -E "s/$CMDLINE/\1/")"
        COMMENT="$(echo ${line} | sed -E "s/$CMDLINE/\2/")"
        RETURNCODE="$(echo ${line} | sed -E "s/$CMDLINE/\3/")"
        echo ">>> python $FILENAME $ARGUMENTS$COMMENT(returncode: $RETURNCODE)" >> "$TARGETFILE"
        python $FILENAME $ARGUMENTS 2>> $TARGETFILE >> "$TARGETFILE"
        if [[ $? == $RETURNCODE ]]; then
            echo >> $TARGETFILE
        else
            cat "$TARGETFILE"
            echo "bad returncode: $? != $RETURNCODE"
            return 1
        fi
    done || return 1
    echo '"""' >> "$TARGETFILE"
    LINES_IN_FILE=$(wc -l < "$FILENAME" | bc)
    tail -n $((LINES_IN_FILE - ${LINES[1]})) "$FILENAME">> "$TARGETFILE"
    echo "done $FILENAME"
    cp "$TARGETFILE" "$FILENAME"
}


shopt -s nullglob
for file in $1*.py; do
    processfile "$file" || (echo "BREAK!!" && exit 1) || exit 1
done
