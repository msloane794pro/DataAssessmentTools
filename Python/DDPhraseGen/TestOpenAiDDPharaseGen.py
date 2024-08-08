# TestOpenAiDDPharaseGet
# DDPhraseGen
# Command line based utility to generate element descriptions and friendly names based upon Data Dictionary input.

from OpenAiDDPhraseGen import OpenAiDDPhraseGen 
from OpenAiDDPhraseGen import PhraseType 

pg = OpenAiDDPhraseGen()

pg.greet()

text = pg.createSessionMessageText('abcdefghijkl', PhraseType.DESCRIPTION.name, 'Drawings', 'ThisTableA', ['Item 1', 'Item 2', 'Item 3'])
print(f'test Case 01:\n{text}\n\n')

text = pg.createSessionMessageText('abcdefghijkl', PhraseType.DESCRIPTION.name, 'Documents', 'ThisTableB', ['Item 4', 'Item 5', 'Item 6'])
print(f'test Case 02:\n{text}\n\n')

text = pg.createSessionMessageText('zyxwbillyraw', PhraseType.DESCRIPTION.name, 'Tracking', 'ThisTableV', ['Item 7', 'Item 8', 'Item 9'])
print(f'test Case 03:\n{text}\n\n')

text = pg.createSessionMessageText('', PhraseType.DESCRIPTION.name, 'Work Flow', 'ThisTableZ', ['Item A', 'Item B', 'Item C'])
print(f'test Case 04:\n{text}\n\n')

text = pg.createSessionMessageText('aeiousometimesy', PhraseType.FRIENDLYNAME.name, '', 'ThisTableA', ['Item 1', 'Item 2', 'Item 3'])
print(f'test Case 05:\n{text}\n\n')
