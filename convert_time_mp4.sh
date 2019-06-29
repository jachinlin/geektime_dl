#!/bin/bash

set -o nounset
set -o errexit

function read_dir(){

    MY_SAVEIFS=$IFS
    # IFS=$(echo -en "\n\b")
    IFS=$'\n'
    for file in `ls $1`
    do
        if [ -d "$1/${file}" ];then
            read_dir "$1/${file}"
        else
            if [ "${file##*.}" != "mp4" ] && [ "${file##*.}" == "ts" ];then
               if [ ! -f "$1/${file}.mp4" ];then
                 /usr/local/bin/ffmpeg -y -i $1"/$file" -c:v libx264 -c:a copy -bsf:a aac_adtstoasc $1"/$file".mp4
               fi
	    fi
        fi
    done
    IFS=$MY_SAVEIFS
}
#读取第一个参数
echo -n "Please enter your mp4/ts download dictionary:"
read mp4_dictionary
read_dir $mp4_dictionary

