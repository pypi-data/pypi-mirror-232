# pip3 install spacy
# python3 -m spacy download zh_core_web_lg
# https://spacy.io/usage
# https://spacy.io/api/span
import spacy
# https://ask.csdn.net/questions/7999119
from spacy.language import Language
# https://pypi.org/project/text2vec/
from text2vec import SentenceModel
# https://blog.csdn.net/hqh131360239/article/details/79061535
import numpy

spacy_gpu = spacy.prefer_gpu()
print("spacy_gpu?", spacy_gpu)

@Language.component("zh_sentencizer")
def zh_sentencizer(doc):
    punct_chars = ['。', '！', '？', '……', '；', '：']
    is_sent_start = True
    for token in doc:
        token.is_sent_start = is_sent_start
        is_sent_start = token.text in punct_chars
    return doc

nlp = spacy.load('zh_core_web_lg')
nlp.add_pipe("zh_sentencizer", before="parser")
print(nlp.pipe_names)

model = SentenceModel('shibing624/text2vec-base-chinese')

def encode(para):
    doc = nlp(para)
    Vector = []
    Text = []
    for sent in filter(lambda x:x.has_vector, doc.sents):
        Vector.append((sent.vector/sent.vector_norm).tolist())
        Text.append(sent.text)
    Vector = numpy.array(Vector)
    if not Vector.shape[0]: return(Vector, Text)

    Vector2 = model.encode(Text)
    Vector2_norm = numpy.linalg.norm(Vector2, axis=1, keepdims=True)
    Vector2 = Vector2/Vector2_norm
    """
    已知：|V2| = 1，|V| = 1
    问题：|(a×V2,b×V)| = 1
    推导：|(a×V2,b×V)|
        = sqrt((a×V2,b×V)⋅(a×V2,b×V))
        = sqrt(|a×V2|^2+|b×V|^2)
        = sqrt(a^2+b^2)
    结论：{(a,b)|a^2+b^2=1}
    例如：{(0.7071,0.7071), (0.8,0.6), ...}
    """
    Vector = numpy.hstack((Vector2 * 0.8, Vector * 0.6))
    return(Vector, Text)
