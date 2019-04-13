#!/bin/bash
# Converts all specified ALAC files to FLAC files with the same path and name.
err=0
for f in "$@"; do
	# Just assume every m4a file specified is ALAC.
	if [[ "$f" != *.m4a ]]; then
		echo "Unsupported file: $f"
		err=1
		continue
	fi
	outfile="${f%.m4a}.flac"
	ffmpeg -i "$f" "$outfile"
	if [[ $? -ne 0 ]]; then
		rm -f "$outfile"
		err=1
		continue
	fi
	# ffmpeg doesn't preserve art. Extract and import the main cover art ourselves.
	mp4art --extract "$f"
	cover=("${f%.m4a}.art[0]."*)
	if [[ -f "$cover" ]]; then
		metaflac --import-picture-from="$cover" "$outfile"
	else
		echo "WARNING no album art in $f"
	fi
	echo "Output: $outfile"
	rm -f "${f%.m4a}.art"*
done
exit $err
