import subprocess as cmdLine
import wave

'''
Ideally the input to espeak would look a little like this:

{
    'Base_voice_parameters': {
        'speed': 3,
        'pitch': 5,
        'voice': 'en',
        'volume': 5}
    'Main_text' : [
        {'Text':'Te', 'speed': 5, 'pitch': 6, 'volume': 2},
        {'xt I wa' }
        {'nt to s'},
        {'ay'}
    ]

'''

'''
    
-f <text file>   Text file to speak

--stdin    Read text input from stdin instead of a file

If neither -f nor --stdin, then <words> are spoken, or if none then text
is spoken from stdin, each line separately.

-a <integer>
           Amplitude, 0 to 200, default is 100
-g <integer>
           Word gap. Pause between words, units of 10mS at the default speed
-k <integer>
           Indicate capital letters with: 1=sound, 2=the word "capitals",
           higher values indicate a pitch increase (try -k20).
-l <integer>
           Line length. If not zero (which is the default), consider
           lines less than this length as end-of-clause
-p <integer>
           Pitch adjustment, 0 to 99, default is 50
-s <integer>
           Speed in approximate words per minute. The default is 175
-v <voice name>
           Use voice file of this name from espeak-data/voices
-w <wave file name>
           Write speech to this WAV file, rather than speaking it directly
-b         Input text encoding, 1=UTF8, 2=8 bit, 4=16 bit 
-m         Interpret SSML markup, and ignore other < > tags
-q         Quiet, don't produce any speech (may be useful with -x)
-x         Write phoneme mnemonics to stdout
-X         Write phonemes mnemonics and translation trace to stdout
-z         No final sentence pause at the end of the text
--compile=<voice name>
           Compile pronunciation rules and dictionary from the current
           directory. <voice name> specifies the language
--ipa      Write phonemes to stdout using International Phonetic Alphabet
--path="<path>"
           Specifies the directory containing the espeak-data directory
--pho      Write mbrola phoneme data (.pho) to stdout or to the file in --phonout
--phonout="<filename>"
           Write phoneme output from -x -X --ipa and --pho to this file
--punct="<characters>"
           Speak the names of punctuation characters during speaking.  If
           =<characters> is omitted, all punctuation is spoken.
--sep=<character>
           Separate phonemes (from -x --ipa) with <character>.
           Default is space, z means ZWJN character.
--split=<minutes>
           Starts a new WAV file every <minutes>.  Used with -w
--stdout   Write speech output to stdout
--tie=<character>
           Use a tie character within multi-letter phoneme names.
           Default is U+361, z means ZWJ character.
--version  Shows version number and date, and location of espeak-data
--voices=<language>
           List the available voices for the specified language.
           If <language> is omitted, then list all voices.

'''



'''

Pty Language Age/Gender VoiceName          File          Other Languages
 2  en-gb          M  english              en            (en-uk 2)(en 2)
 3  en-uk          M  english-mb-en1       mb/mb-en1     (en 2)
 2  en-us          M  english-us           en-us         (en-r 5)(en 3)
 5  en-sc          M  en-scottish          other/en-sc   (en 4)
 5  en             M  default              default       
 5  en-uk-north    M  english-north        other/en-n    (en-uk 3)(en 5)
 5  en-uk-rp       M  english_rp           other/en-rp   (en-uk 4)(en 5)
 5  en-us          M  us-mbrola-2          mb/mb-us2     (en 7)
 5  en-us          F  us-mbrola-1          mb/mb-us1     (en 8)
 5  en-us          M  us-mbrola-3          mb/mb-us3     (en 8)
 9  en             M  en-german            mb/mb-de4-en  
 9  en             F  en-german-5          mb/mb-de5-en  
 9  en             M  en-greek             mb/mb-gr2-en  
 9  en             M  en-romanian          mb/mb-ro1-en  
 5  en-uk-wmids    M  english_wmids        other/en-wm   (en-uk 9)(en 9)
10  en             M  en-dutch             mb/mb-nl2-en  
10  en             F  en-french            mb/mb-fr4-en  
10  en             M  en-french            mb/mb-fr1-en  
10  en             F  en-hungarian         mb/mb-hu1-en  
10  en             F  en-swedish-f         mb/mb-sw2-en  
 5  en-wi          M  en-westindies        other/en-wi   (en-uk 4)(en 10)
11  en             M  en-afrikaans         mb/mb-af1-en  
11  en             F  en-polish            mb/mb-pl1-en  
11  en             M  en-swedish           mb/mb-sw1-en  


'''

speech1 = "This is"
speech2 = "why"
speech3 = "I think this wont work"
file1 = 'File1.wav'
file2 = 'File2.wav'
file3 = 'File3.wav'



command = 'espeak -w' + file1 + ' -p 99 -g 0 ' + chr(34) + speech1 + chr(34)
cmdLine.run(command, shell=True, capture_output=True, text=True)

command = 'espeak -w' + file2 + ' -p 60 -s 50 -g 0 ' + chr(34) + speech2 + chr(34)
cmdLine.run(command, shell=True, capture_output=True, text=True)

command = 'espeak -w' + file3 + ' -p 99 -g 0 ' + chr(34) + speech3 + chr(34)
cmdLine.run(command, shell=True, capture_output=True, text=True)

#Combines list of wav files into one

infiles = ['File1.wav', 'File2.wav', 'File3.wav']
outfile = 'sounds.wav'

data = []
for infile in infiles:
    w = wave.open(infile, 'rb')
    data.append( [w.getparams(), w.readframes(w.getnframes())] )
    w.close()

output = wave.open(outfile, 'wb')
output.setparams(data[0][0])
for i in range(len(data)):
    output.writeframes(data[i][1])
output.close()
