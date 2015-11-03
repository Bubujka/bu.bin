#!/bin/bash

INRES="1600x900" # input resolution
OUTRES="1600x900" # output resolution
FPS="25" # target FPS
GOP="50" # i-frame interval, should be double of FPS,
GOPMIN="25" # min i-frame interval, should be equal to fps,
THREADS="2" # max 6
CBR="1100k" # constant bitrate (should be between 1000k - 3000k)
QUALITY="veryfast" # one of the many FFMPEG preset
AUDIO_RATE="44100"

cd ~/.db/screencasts
FILE=$(date +'%Y.%m.%d-%H.%M.%S').flv
avconv \
  -f x11grab\
  -s "$INRES"\
  -r "$FPS"\
  -i :0.0\
  -f alsa\
  -i hw:0\
  -f flv\
  -ac 2\
  -ar $AUDIO_RATE \
  -vcodec libx264\
  -keyint_min 3\
  -b:v $CBR\
  -minrate $CBR\
  -maxrate $CBR\
  -pix_fmt yuv420p \
  -s $OUTRES\
  -preset $QUALITY\
  -acodec mp3\
  -threads $THREADS \
  -bufsize $CBR \
  - | tee $FILE | avconv -i - -f flv -c copy -bufsize $CBR "rtmp://eumedia1.livecoding.tv:1935/livecodingtv/$STREAM_KEY" 
  #-acodec copy -vcodec copy file.flv

