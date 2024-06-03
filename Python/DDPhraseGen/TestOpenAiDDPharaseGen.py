# TestOpenAiDDPharaseGet
# DDPhraseGen
# Command line based utility to generate element descriptions and friendly names based upon Data Dictionary input.

from OpenAiDDPhraseGen import OpenAiDDPhraseGen 
from OpenAiDDPhraseGen import PhraseType 

pg = OpenAiDDPhraseGen()

pg.greet()

text = pg.createSessionMessageText('abcdefghijkl', PhraseType.DESCRIPTION, 'ThisTableA', ['Item 1', 'Item 2', 'Item 3'])
print(text)

text = pg.createSessionMessageText('abcdefghijkl', PhraseType.DESCRIPTION, 'ThisTableB', ['Item 4', 'Item 5', 'Item 6'])
print(text)

text = pg.createSessionMessageText('zyxwbillyraw', PhraseType.DESCRIPTION, 'ThisTableV', ['Item 7', 'Item 8', 'Item 9'])
print(text)

text = pg.createSessionMessageText('', PhraseType.DESCRIPTION, 'ThisTableZ', ['Item A', 'Item B', 'Item C'])
print(text)

text = pg.createSessionMessageText('aeiousometimesy', PhraseType.FRIENDLYNAME, 'ThisTableA', ['Item 1', 'Item 2', 'Item 3'])
print(text)
