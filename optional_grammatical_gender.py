'''
Copyleft Alexander Poone 2024 Edutainment.

Adds indefinite article with grammatical gender in front of each item/block name for learners of languages with gender. The gender is obtained from re-structured Wiktionary dumps.

Uses the indefinite article instead of definite article because of epenthesis and elision rules.
'''

from glob import glob
from json import loads
from os.path import exists, expanduser
from pickle import dump
from re import sub
from traceback import format_exc
from zipfile import ZipFile

from requests import get

##################################################
#    User Config
##################################################
LANG = 'fr_fr'

##################################################
#    Constants
##################################################
CURSEFORGE_INSTALLED = exists(expanduser('~/curseforge/minecraft'))    # False
LEAPFROG = '1.21'                               # Leapfrog to the latest translation, e.g., 1.20.6 using 1.21's updated translation.
SUPPORTED_MOD_LIST = ('advancementframes',      # It doesn't matter if some mods are not installed, the script will skip them.
            'betterlily',
            'betterpvp',
            'biomesoplenty',
            'cfm',
            'comforts',
            'croptopia',
            'curios',
            'dummmmmmy',
            'explorerscompass',
            'farmersdelight',
            'goated',
            'hauntedharvest',
            'heartstone',
            'jade',
            'jeed',
            'jei',
            'labels',
            'map_atlases',
            'mcw-bridges',
            'mcw-doors',
            'mcw-fences',
            'mcw-lights',
            'mcw-paintings',
            'mcw-paths',
            'mcw-roofs',
            'mcw-trapdoors',
            'mcw-windows',
            'modmenu',
            'moonlight',
            'moyai',
            'naturescompass',
            'oculus',
            'polytone',
            'sereneseasons',
            'sleep_tight',
            'smarterfarmers',
            'snowyspirit',
            'supplementaries',
            'suppsquared',
            'terralith',
            'toughasnails',
            'wthit',
            'xaeros_minimap',)

if CURSEFORGE_INSTALLED:
    MC_HOME = expanduser('~/curseforge/minecraft/Install')
    MC_MODS = expanduser(
        f'~/curseforge/minecraft/Instances/{VERSION_TO_BE_PATCHED}')
else:
    MC_HOME = MC_MODS = expanduser('~/AppData/Roaming/.minecraft')

##################################################
#    Build Knowledge Base
##################################################
def build_knowledge_base(VERSION_TO_BE_PATCHED = '1.21'):
    lang_directory = None

    if LANG[:2] == 'fr':
        lang_directory = 'French'
    elif LANG[:2] == 'es':
        lang_directory = 'Spanish'
    elif LANG[:2] == 'de':
        lang_directory = 'German'
    else:
        raise Exception('⛔ Language not supported.')

    # TODO: find latest file, not hardcoding '5' and '1.20'
    # hash = loads(open(expanduser('~/AppData/Roaming/.minecraft/assets/indexes/1.19.json'), 'r', encoding='utf-8').read())['objects']['minecraft/lang/en_gb.json']['hash']
    hash = loads(open(f'{MC_HOME}/assets/indexes/16.json', 'r',
                 encoding='utf-8').read())['objects'][f'minecraft/lang/{LANG}.json']['hash']
    print('Hash found: ', hash)

    trans = loads(open(
        f'{MC_HOME}/assets/objects/{hash[:2]}/{hash}', 'r', encoding='utf-8').read())

    words = [trans[k].split(' ')[0].lower() if lang_directory != 'German' else trans[k].split(' ')[0].split('-')[-1] for k in trans if len(trans[k].split(' ')[0]) > 2 and (k.startswith(
        'item.minecraft') or k.startswith('block.minecraft') or k.startswith('entity.minecraft'))]

    for mod in SUPPORTED_MOD_LIST:
        try:
            mod_trans_json_str = sub('//.*', '', ZipFile(glob(f'{MC_MODS}/mods/{mod}*.jar')[0]).open(f'assets/{mod.replace("-", "").replace("trap", "trp").replace(
                "wthit", "waila").replace("xaeros_", "xaero").replace("betterpvp", "xaerobetterpvp").replace("oculus", "iris")}/lang/{LANG}.json').read().decode('utf-8'))
            mod_trans = loads(mod_trans_json_str)
            new = sorted(set([mod_trans[k].split(' ')[0].lower() if lang_directory != 'German' else mod_trans[k].split(' ')[0].split('-')[-1] for k in mod_trans if len(mod_trans[k].split(
                ' ')[0]) > 2 and (k.startswith('item.') or k.startswith('block.') or k.startswith('entity.'))]))
            print(new)
            words += new
        except Exception as e:
            print(mod, format_exc())
    words = sorted(set(words))
    print(words)

    worddict = {}
    for word in words:
        print(word)
        try:
            url = f'https://kaikki.org/dictionary/{lang_directory}/meaning/{word[0]}/{word[:2]}/{word}.json'
            print(url)
            res = get(url)
            tags = loads([x for x in res.text.split('\n') if x.startswith(
                '{"pos": "noun')][0])['senses'][0]['tags']
            out_display = 'p' if 'plural' in tags else (
                'm' if 'masculine' in tags else ('n' if 'neuter' in tags else ('f' if 'feminine' in tags else None)))
            worddict[word] = out_display
        except:
            print('🚫', word, 'failed')
    with open(f'knowledgebase/mc_{LANG}.pickle', 'wb') as f:
        dump(worddict, f)
    print(worddict)

if __name__ == '__main__':
    build_knowledge_base()