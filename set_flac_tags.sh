#!/bin/bash
metaflac --export-tags-to=tags.txt "$1"
awkprog='
BEGIN {
	FS="="
	IGNORECASE=1
	matched=0
}
{
	if ($1 != name) {
		print $0
	} else if (matched == 0) {
		if (length(val) > 0)
			print $1"="val
		matched=1
	}
}
END {
	if (matched == 0 && length(val) > 0)
		print name"="val
}
'
for tagspec in "${@:2}"; do
	tagname="${tagspec%%=*}"
	tagval="${tagspec#*=}"
	# Sorting like this isn't perfect: "ALBUM=" should go before "ALBUMARTIST="
	awk -v "name=$tagname" -v "val=$tagval" "$awkprog" tags.txt | sort > tags2.txt
	mv tags2.txt tags.txt
done
metaflac --remove-all-tags --import-tags-from=tags.txt "$1"
rm -f tags.txt
