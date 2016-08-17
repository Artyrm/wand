#!/usr/bin/env python

from os.path import basename

import json

KNOWLEDGE = 'generation_knowledge.json'

OUTPUT = '../src_c/knowledge'

PREFIX = 'stroke'

STROKE_MAX_LENGTH = 256


def stroke_const_name(key):
    return '{prefix}_{key}'.format(prefix=PREFIX.upper(), key=key.upper())


def format_define_to_c(name, value, comment=None):
    comment = ' // ' + comment if comment is not None else ''
    return '''#define {name} {value}{comment}
'''.format(name=name, value=value,
           comment=comment)


def format_formated_strokes_to_c(value):
    data = ',\n'.join(['        {%s}' % ', '.join(['% 2.5f' % x for x in line])
                      for line in value])

    text = '''    {{\n{data}\n    }}'''
    return text.format(data=data)


def convert_knowledge(knowledge):

    strokes = knowledge['strokes']

    h_text = ('/*\n * {filename}.h\n * autogenerated\n*/\n\n'
              .format(filename=basename(OUTPUT)))

    c_text = ('/*\n * {filename}.cpp\n * autogenerated\n*/\n\n'
              .format(filename=basename(OUTPUT)))

    c_text += '#include "{filename}.h"\n\n'.format(filename=basename(OUTPUT))

    h_text += '#ifndef STROKES_H_\n#define STROKES_H_\n\n'

    h_text += format_define_to_c('DIMENTION', 3)

    h_text += format_define_to_c('STROKE_MAX_LENGTH', 256)

    h_text += format_define_to_c('MAX_ERROR', 0.2)

    h_text += format_define_to_c('SEGMENTATION', knowledge['segmentation'])

    h_text += format_define_to_c('STROKES_COUNT', len(strokes))

    h_text += format_define_to_c('MIN_DIMENTION', knowledge['splitting']['min_dimention'])
    h_text += format_define_to_c('ACCELERATION_TIME_CONST', knowledge['splitting']['acceleration_time_const'])

    h_text += format_define_to_c('GYRO_MIN', knowledge['splitting']['gyro_min'])
    h_text += format_define_to_c('GYRO_TIMEOUT', knowledge['splitting']['gyro_timeout'])
    h_text += format_define_to_c('MIN_STROKE_LENGTH', knowledge['splitting']['min_length'])
    h_text += format_define_to_c('COMPARE_LIMIT', knowledge['splitting']['compare_limit'])

    header = ''

    formated_strokes = []

    for index in xrange(len(strokes)):
        name = str(index)
        value = strokes[name]
        formated_strokes += [format_formated_strokes_to_c(value)]

    formated_strokes = '''
const float STROKES[STROKES_COUNT][SEGMENTATION][DIMENTION + 1] = {{
{formated_strokes}
}};'''.format(formated_strokes=',\n'.join(formated_strokes))

    h_text += header + '\n'

    h_text += 'extern const float STROKES[STROKES_COUNT][SEGMENTATION][DIMENTION + 1];\n'
    h_text += 'extern const float MAGNETS_BOUNDARIES[2][DIMENTION];\n'

    c_text += formated_strokes

    c_text += '''
const float MAGNETS_BOUNDARIES[2][DIMENTION] =
{formated_strokes}
;'''.format(formated_strokes=format_formated_strokes_to_c(knowledge['magnet_boundaries']))

    c_text += '\n'

    h_text += '\n\n#endif\n'

    return h_text, c_text

if __name__ == '__main__':
    with open(KNOWLEDGE, 'r') as f:
        knowledge = json.load(f)

    h_text, c_text = convert_knowledge(knowledge)

    with open(OUTPUT + '.h', 'w') as f:
        f.write(h_text)

    with open(OUTPUT + '.cpp', 'w') as f:
        f.write(c_text)
