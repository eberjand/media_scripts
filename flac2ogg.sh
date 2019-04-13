#!/bin/bash
# Convert a single flac file to ogg, retaining metadata and artwork
# Usage: flac2ogg.sh file.flac
# Depends: flac vorbis-tools imagemagick
outfile="${1%.flac}.ogg"
echo "  Input=$1"
echo "  Output=$outfile"

art="$(mktemp)"

oggenc -o "$outfile" -q5 "$1"

metaflac --export-picture-to="$art" "$1" 2>/dev/null
if [[ $? -ne 0 ]]; then
	echo "$1 has no artwork."
else
	oggart.sh "$outfile" "$art"
fi

rm -f "$art"
