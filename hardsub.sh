#!/bin/bash
#Simplified with just mpv:
#mpv file.mkv --o=out.mp4 --ovcopts=crf=26
hexcrc() {
	cksfv "$1" | awk '{
		if (substr($0,0,1) != ";")
			print substr($0, length($0)-7, 8)
	}'
}
input="$(realpath "$1")"
crc=$(hexcrc "$1")
tmpdir="${tmpdir-tmp}/${crc}"
x264args="--demuxer y4m --threads auto --bitrate 1000 -o out.264 hardsub.yuv"
mkdir -p "$tmpdir"
cd "$tmpdir"
mpv --o=hardsub.yuv --oautofps --oneverdrop "$input"
x264 --pass 1 $x264args
x264 --pass 2 $x264args
rm -f hardsub.yuv
mkvextract tracks "$input" 1:audio
#TODO use mkvextract output to determine whether audio is flac or aac
#Extracting track 1 with CodecID 'A_FLAC' to the file 'audio.' Container format: raw data
flac -c -d audio | faac -o out.aac -
#flac -d -o p1.wav --skip=00:00.00 --until=00:00.00 audio
#sox p1.wav ../op1.wav p2.wav ../ed1.wav p3.wav
#mv audio out.aac
MP4Box -fps 23.976 -add out.264 -add out.aac out.mp4
#mkvmerge -o hardsub.mkv out.264
crc=$(hexcrc out.mp4)
destname="$(basename "$input")"
destname="$(echo "$destname" | sed 's/\[[A-F0-9]\{8\}\]/\['${crc}'\]/')"
destname="$(dirname "$input")/$destname"
destname="${destname/.mkv/.mp4}"
cd -
mv "${tmpdir}/out.mp4" "$destname"
echo "Created: $destname"
#rm -r "$tmpdir"
