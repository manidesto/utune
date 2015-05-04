from __future__ import unicode_literals
import os
from subprocess import call
import json

EDITOR = os.environ.get('EDITOR', 'vim')
TEMPMETADATA_FILENAME = 'tempmetadata.json'

class Metamine:

    def __init__(self, filename = None):
        self.userfilename = './' + filename if filename else None

    def __get_from_user__(self):
        #empty metadata
        metadata = {}
        metadata['title'] = ''
        metadata['artist'] = ''
        metadata['album_artist'] = ''
        metadata['album'] = ''
        metadata['genre'] = 'Soundtrack'
        metadata['date'] = '2015'
        metadata['album_art_link'] = ''
        metadata['lyricist'] = ''

        #dump the empty metadata to temp metadata file
        with open(TEMPMETADATA_FILENAME, 'w') as tempfile:
            json.dump(metadata, tempfile, indent=4)

        #open the editor for the user to input the metadata
        call([EDITOR, TEMPMETADATA_FILENAME])

        #load the edited metadata
        metadata = self.__get_from_temp__()

        #delete the temp meta data file
        os.remove(TEMPMETADATA_FILENAME)

        return metadata

    def __get_from_temp__(self):
        with open(TEMPMETADATA_FILENAME) as metafile:
            try:
                return json.load(metafile)
            except ValueError as e:
                print('Invalid metadata %s' % e)
                #TODO ask the user if he wants to edit or abort
                call([EDITOR, TEMPMETADATA_FILENAME])
                return self.__get_from_temp__()

    def get_metadata(self):
        if self.userfilename is None:
            metadata = self.__get_from_user__()
        elif os.path.isfile(self.userfilename) is not True:
            metadata = self.__get_from_user__()

        #else read metadata from file
        with open(self.userfilename) as metafile:
            try:
                metadata = json.load(metafile)
            except ValueError as e:
                print ('Invalid metadata %s' % e)
                metafile.close()

                #TODO: ask the user wether he wants to 
                # edit an empty data or this file

                call([EDITOR, self.userfilename])
                metadata = self.get_metadata()


        #Extract lyrics if given
        if 'lyrics' in metadata :
            lyrics = metadata['lyrics']
        else:
            lyrics = u""

        #Add lyricist info in lyrics
        if metadata['lyricist'] :
            metadata['lyrics'] = u"Lyrics by " + metadata['lyricist'] + "\n" + lyrics

        return metadata


