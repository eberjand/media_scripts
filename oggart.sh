#!/bin/bash
# Adds album art to an ogg file
# Usage: oggart.sh file.ogg cover.jpg
# Depends: vorbis-tools imagemagick
#echo "  Input OGG=$1"
#echo "  Input art=$2"

outfile="$1"
art="$2"
artfull="$(mktemp)"
commfile="$(mktemp)"

artmime="$(file -b --mime-type "$art")"
read artwidth artheight <<<$(identify -format '%w %h' "$art")

# The picture starts with a header with several 32-bit numbers and strings
# pictureType(3=frontCover) mimeLength mimeText
printf "%08x" 3 $(echo -n "$artmime" | wc -c) | xxd -r -p > "$artfull"
echo -n "$artmime" >> "$artfull"
# descriptionLen descriptionText width height colordepth colorcount filesize
#printf "%08x" 0 $artwidth $artheight 0 0 $(wc -c < "$art") | xxd -r -p > "$artfull"
printf "%08x" 0 0 0 0 0 $(wc -c < "$art") | xxd -r -p >> "$artfull"
# image data
cat "$art" >> "$artfull"
# Print the base64 in a comment file
echo "metadata_block_picture=$(base64 -w 0 "$artfull")" > "$commfile"

vorbiscomment -a -c "$commfile" "$outfile"
echo "Added album art: ${artwidth}x${artheight} $artmime"

rm -f "$artfull" "$commfile"
