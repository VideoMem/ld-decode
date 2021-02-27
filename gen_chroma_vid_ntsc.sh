#!/bin/sh

rm -f $1_doc.tbc
rm -f $1_doc.tbc.json
rm -f $1_chroma_doc.tbc
rm -f $1.rgb
rm -f $1_chroma.rgb
rm -f $1.mkv
rm -f $1_chroma.mkv

ld-dropout-correct $1.tbc $1_doc.tbc
ld-dropout-correct -i --input-json $1.tbc.json $1_chroma.tbc $1_chroma_doc.tbc

ld-chroma-decoder -f mono -p yuv $1_doc.tbc $1.rgb
ld-chroma-decoder -f ntsc2d -p yuv --ntsc-phase-comp --input-json $1.tbc.json $1_chroma_doc.tbc $1_chroma.rgb

ffmpeg -f rawvideo -r 30000/1001 -pix_fmt yuv444p16 -s 760x488 -i $1_chroma.rgb -r 30000/1001 -pix_fmt gray16 -s 760x488 -i $1.rgb -filter_complex "[0:v]format=yuv444p16le[chroma];[1:v]format=yuv444p16le[luma];[chroma][luma]mergeplanes=0x100102:yuv444p16le[output]" -map "[output]":v -c:v libx264 -qp 0 -pix_fmt yuv444p16le -top 1 -color_range tv -color_primaries smpte170m -color_trc smpte170m -colorspace smpte170m -aspect 4:3 -y $1.mkv
#ffmpeg -f rawvideo -r 30000/1001 -pix_fmt rgb48 -s 760x488 -i $1.rgb -c:v libx264 -qp 0 -pix_fmt yuv444p16le -top 1 -color_range tv -color_primaries smpte170m -color_trc smpte170m -colorspace smpte170m -aspect 4:3 -y $1_luma.mkv
#ffmpeg -f rawvideo -r 30000/1001 -pix_fmt rgb48 -s 760x488 -i $1_chroma.rgb -c:v libx264 -qp 0 -pix_fmt yuv444p16le -top 1 -color_range tv -color_primaries smpte170m -color_trc smpte170m -colorspace smpte170m -aspect 4:3 -y $1_chroma.mkv
