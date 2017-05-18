import re

class States(object):
    wanttitle=1
    wantschool=2
    gotschool=3
    gotproperty=4
    gottext=5
    gotpostproperty=6


SCHOOLS = [
    'Abjuration',
    'Conjuration',
    'Divination',
    'Enchantment',
    'Evocation',
    'Illusion',
    'Necromancy',
    'Transmutation',
    'Universal',
]

SPELL_PROPERTIES = {
    'Level',
    'Components',
    'Casting Time',
    'Range',
    'Area',
    'Duration',
    'Saving Throw',
    'Spell Resistance',
    'Effect',
    'Target',
    'Targets',
}

SPELL_POSTPROPERTIES = {
    'XP Cost',
    'Arcane Focus',
    'Arcane Material Component',
    'Divine Focus',
    'Divine Material Component',
    'Focus',
    'Material Component',
}

SCHOOL_REGEX = re.compile(
    r'(' + r'|'.join(SCHOOLS) + r')'
    + r'\s*'

    + r'('
    + r'\(\s*'
    + r'[a-zA-Z]+'
    + r'(,\s*[a-zA-Z]+)*'
    + r'\s*\)\s*)?'

    + r'('
    + r'\[\s*'
    + r'[a-zA-Z]+'
    + r'(,\s*[a-zA-Z]+)*'
    + r'\s*\]\s*)?'
)

MACRO_TEMPLATE = '&{{template:DnD35StdRoll}} {{{{spellflag=true}}}} {{{{name= @{{character_name}} casts {title}}}}} {{{{School:={school} }}}} {{{{Level:={level} }}}} {props} {{{{Conc.:= [[ 1d20 + [[ @{{concentration}} ]] ]] }}}} {{{{check={check}}}}} {{{{checkroll={checkroll}}}}} {{{{notes={text} ({book})}}}}'

def __index(instr, inchr):
    for c in range(len(instr)):
        if instr[c] == inchr:
            return c
    else:
        return None

class Spell(object):
    def __init__(self, title, school, properties, text):
        self.title = title
        self.school = school
        self.properties,self.propertyorder = Spell.__parseproperties(properties)
        self.text = text
        self.book = 'BOOK ###'
        self.check = 'check'
        self.checkroll = 'checkroll'

    def __repr__(self):
        return '(Spell: {0} {1} with properties {2})'.format(self.title, self.school, self.properties)

    def classlevel(self, cl):
        if 'Level' not in self.properties:
            return None

        classes = self.properties['Level'].split(',')
        for c in classes:
            cs = c.strip()
            if cs.startswith(cl + ' '):
                return int(cs.split(' ')[1].strip())
        return None

    def __spellfocus(self):
        return 'sf-'+self.school.split(' ')[0].strip().lower()

    @staticmethod
    def __parseproperties(props):
        retvald = dict()
        retvalo = list()

        for p in props:
            delim = __index(p, ':')
            k,v = p[:delim],p[delim+1:].strip()
            retvald[k] = v
            retvalo.append(k)

        return (retvald, retvalo)

    @staticmethod
    def isschoolvalid(school):
        return SCHOOL_REGEX.match(school) is not None

    def __savedc(self, cl):
        if 'Saving Throw' not in self.properties:
            return 'INVALID'

        save = self.properties['Saving Throw']
        if save == 'None':
            return save
        return (save
                + ' (DC [[ @{{spelldc{level}}} + @{{{spellfocus}}} ]])'.format(
                    level=cl,
                    spellfocus=self.__spellfocus(),
                )
        )

    def textsummary(self):
        return self.text.split('.')[0] + '.'

    def __macroproperties(self, cl):
        props = list()
        BLACKLIST = 'Level'
        SPECIALS = {
            'Saving Throw': self.__savedc(self.classlevel(cl)),
        }
        ABBREV = {
            'Components': 'Comp.',
            'Casting Time': 'Cast',
            'Duration': 'Dur.',
            'Saving Throw': 'Save',
            'Spell Resistance': 'SR',
        }
        for p in self.propertyorder:
            if p in BLACKLIST:
                continue
            if p in SPECIALS:
                formatted = SPECIALS[p]
            else:
                formatted = self.properties[p]
            if p in ABBREV:
                abbrev = ABBREV[p]
            else:
                abbrev = p
            props.append('{{{{{}:={} }}}}'.format(abbrev, formatted))
        return ' '.join(props)

    def macro(self, cl):
        return MACRO_TEMPLATE.format(
            title=self.title,
            school=self.school,
            level=self.classlevel(cl),
            props=self.__macroproperties(cl),
            text=self.textsummary(),
            book=self.book,
            check=self.check,
            checkroll=self.checkroll,
        )

def isschoolstart(line):
    for s in SCHOOLS:
        if line.startswith(s):
            return True
    else:
        return False

def __startsupper(c):
    return c[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def ispropertystart(line):
    if (__startsupper(line)
        and ':' in line
        and line.split(':')[0].strip() in SPELL_PROPERTIES):
        return True
    else:
        return False

def ispostpropertystart(line):
    if (__startsupper(line)
        and ':' in line
        and line.split(':')[0].strip() in SPELL_POSTPROPERTIES):
        return True
    else:
        return False

def istextstart(line):
    if __startsupper(line):
        return True
    else:
        return False

def parse(lines):
    state = States.wanttitle

    accum = ''
    title = None
    school = None
    properties = list()

    for line in lines.split('\n'):
        cleanline = line.strip()
        if len(cleanline) == 0:
            continue

        if state == States.wanttitle:
            accum = cleanline
            state = States.wantschool
        elif state == States.wantschool:
            if isschoolstart(cleanline):
                title = accum.strip()
                accum = cleanline
                state = States.gotschool
            else:
                accum = accum + ' ' + cleanline
        elif state == States.gotschool:
            if ispropertystart(cleanline):
                if not Spell.isschoolvalid(accum.strip()):
                    raise Exception('Invalid school "' + accum + '"')
                school = accum.strip()
                accum = cleanline
                state = States.gotproperty
            else:
                accum = accum + ' ' + cleanline
        elif state == States.gotproperty:
            if ispropertystart(cleanline):
                properties.append(accum.strip())
                accum = cleanline
            elif istextstart(cleanline):
                properties.append(accum.strip())
                accum = cleanline
                state = States.gottext
            else:
                accum = accum + ' ' + cleanline
        elif state == States.gottext:
            if ispostpropertystart(cleanline):
                text = accum.strip()
                accum = cleanline
                state = States.gotpostproperty
            else:
                accum = accum + ' ' + cleanline
        elif state == States.gotpostproperty:
            if ispostpropertystart(cleanline):
                properties.append(accum.strip())
                accum = cleanline
            else:
                accum = accum + ' ' + cleanline

    if state == States.gottext:
        text = accum.strip()
    elif state == States.gotpostproperty:
        properties.append(accum.strip())

    s = Spell(title, school, properties, text)

    return s


def setup():
    document.getElementById('page').value = 'PH ###'
    document.getElementById('check').value = 'Target gains'
    document.getElementById('checkroll').value = (
        '[[ 1d1+{{@{{casterlevel}},10}}dh1 ]] quatloos.'
    )

    document.getElementById('recalculate').addEventListener('mousedown', recalculate)
    document.getElementById('notes').addEventListener('input', update)
    document.getElementById('page').addEventListener('input', update)
    document.getElementById('check').addEventListener('input', update)
    document.getElementById('checkroll').addEventListener('input', update)

GLOBAL_SPELL = None
def recalculate():
    global GLOBAL_SPELL
    GLOBAL_SPELL = parse(document.getElementById('spelltext').value)
    document.getElementById('notes').value = GLOBAL_SPELL.textsummary()
    update()

def validclass():
    document.getElementById('classinfo').textContent = ''

def invalidclass():
    document.getElementById('classinfo').textContent = 'Available classes: ' + GLOBAL_SPELL.properties.Level

def update():
    GLOBAL_SPELL.text = document.getElementById('notes').value
    GLOBAL_SPELL.book = document.getElementById('page').value
    GLOBAL_SPELL.check = document.getElementById('check').value
    GLOBAL_SPELL.checkroll = document.getElementById('checkroll').value

    c = document.getElementById('class').value
    if GLOBAL_SPELL.classlevel(c) is not None:
        validclass()
        document.getElementById('macro').value = GLOBAL_SPELL.macro(c)
    else:
        invalidclass()

setup()
