import re

'''
符合以下四个特征的正文，称为formal正文：
 1）段落是由'\n\n'分割的；或
 2）段落是由'\n\t'分割的；或
 3) 段落是由'\n'分割的；
 4）段落内'\s+'==' '。
'''
def formal(doc, sep='\n'):
    pattern = {
        '\n'  : r'\n\s*\n',
        '\n\n': r'\n\s+',
        '\n\t': r'\s*\n'
    }
    paras = re.split(pattern[sep], doc.strip())
    Paras = []
    for para in paras:
        if sep=='\n':
            Paras.extend(formal(para, sep='\n\n'))
        elif sep=='\n\n':
            Paras.extend(formal(para, sep='\n\t'))
        elif sep=='\n\t':
            Paras.append({
                'text': re.sub(r'\s+', ' ', para),
                'sep': '\n'
            })
    if len(Paras): Paras[-1]['sep'] = sep
    return Paras

def parse_url(doc):
    paras = re.split(r'!?\[([^]]*)\]\(([^)]*)\)', doc)
    Paras = []
    _prev = ''
    for i, para in enumerate(paras):
        if para:
            if i % 3 != 2:
                _prev += para
            elif not _prev:
                para = re.sub(r'\s+("[^"]*"|\'[^\']*\')?\s*', '', para)
                Paras.append({
                    'image': para.replace('\\\\', '/'),
                    'sep': '\n'
                })
        elif i % 3 == 1 and _prev:
            Paras.extend(formal(_prev))
            _prev = ''
    else:
        if _prev:
            Paras.extend(formal(_prev))
    return Paras

def parse(doc, kind='code'):
    regular = {
        'code' : r'(\n```[^\0]*?\n```\n)',
        'table': r'((?:\n[ \t]*\|.+\|[ \t]*){3,}\n)'
    }
    paras = re.split(regular[kind], doc)
    Paras = []
    for i, para in enumerate(paras):
        if not para: continue
        if not i % 2:
            Paras.extend(
                parse(para, kind='table') if kind=='code' else parse_url(para)
            )
        else:
            Paras.append({
                kind: para,
                'sep': '\n'
            })
    return Paras

def stringify(paras, pages=None):
    s = ''
    for i, para in enumerate(paras):
        if pages and i not in pages: continue
        if 'text' in para:
            s += para['text']
        if 'image' in para:
            s += f"![]({para['image']})"
        if 'table' in para:
            s += para['table']
        if 'code' in para:
            s += para['code']
        s += para['sep']
    return s
