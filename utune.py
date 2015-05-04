#! /usr/bin/env python

from __future__ import unicode_literals
import os
import sys
import getopt
import urllib
import youtube_dl
import json
from metamine import Metamine
import eyed3
import mimetypes

def is_url_image(url):
    mimetype,encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))

def add_metadata(audiofile, metafile=None):
    metadata = Metamine(metafile).get_metadata()
    print(json.dumps(metadata, indent = 4))
    audiofile = eyed3.load(audiofile)
    audiofile.tag.title = metadata['title']
    audiofile.tag.artist = metadata['artist']
    audiofile.tag.album_artist = metadata['album_artist']
    audiofile.tag.album = metadata['album']
    audiofile.tag.genre = metadata['genre']
    audiofile.tag.recording_date = metadata['date']

    #check for album art link
    cover_link = metadata['album_art_link']
    if is_url_image(cover_link):
        mimetype,encoding = mimetypes.guess_type(cover_link)
        cover = urllib.urlopen(cover_link).read()
        audiofile.tag.images.set(3, cover, mimetype, metadata['album'])

    #save the tag
    audiofile.tag.save()

    return metadata['title']

def download_audio(link):
    #youtube-dl options
    options = {
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320'
            }],
        'outtmpl': 'temp.%(ext)s',
        'format': 'bestaudio/best'
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([link])

    return 'temp.mp3'

def main(argv):
    metafile = None
    link = None
    try:
        opts, args = getopt.getopt(argv, 'm:l:', ["metadata=", "link="])
    except getopt.GetoptError as e:
        print('Something went wrong %s' % e)
        return 2

    for opt, arg in opts:
        if opt in ('-m', '--metadata'):
            print('metafile = ' + arg)
            metafile = arg
        elif opt in ('-l', '--link'):
            link = arg

    if link is None:
        link = raw_input('link: ')

    print('downloading audio')
    temp_audio = download_audio(link)

    print('Adding metadata')
    title = add_metadata(temp_audio, metafile)

    filename = title + ".mp3"
    os.rename(temp_audio, filename)
    print('Enjoy the song :' + filename)

if __name__ == "__main__":
    main(sys.argv[1:])
