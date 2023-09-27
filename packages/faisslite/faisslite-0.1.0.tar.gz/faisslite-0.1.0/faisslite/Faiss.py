from faisslite.encode import encode
# https://zhuanlan.zhihu.com/p/107241260
# https://zhuanlan.zhihu.com/p/350957155
# https://ispacesoft.com/85864.html
# https://zhuanlan.zhihu.com/p/530958094
import faiss
import os, json

faiss_gpu = faiss.get_num_gpus()
print("faiss_gpu=", faiss_gpu)

class Faiss:
    save_dir = '.'
    def __init__(self, name):
        self.faiss_path = f'{Faiss.save_dir}/{name}.index'
        if not os.path.exists(self.faiss_path):
            self.faiss_index = None
            self.sents = []
            self.paras = []
            self.docs = {}
        else:
            self.load()

    def cpu_to_gpu(self):
        res = faiss.StandardGpuResources()
        self.faiss_index = faiss.index_cpu_to_gpu(res, 0, self.faiss_index)

    def gpu_to_cpu(self):
        self.faiss_index = faiss.index_gpu_to_cpu(self.faiss_index)

    def add(self, para):
        Vector, Text = encode(para)
        if not Vector.shape[0]: return
        if not self.faiss_index:
            # L2 欧几里得距离（空间距离）
            # IP 内积算法（Inner Product）
            self.faiss_index = faiss.IndexFlatIP(Vector.shape[1])
            if faiss_gpu > 0: self.cpu_to_gpu()
        self.faiss_index.add(Vector)
        self.sents.extend(Text)
        assert self.faiss_index.ntotal == len(self.sents)

    def add_doc(self, source, doc):
        if source in self.docs: return
        doc['start'] = len(self.paras)
        for page, para in enumerate(doc['paras']):
            if 'text' not in para: continue
            start = len(self.sents)
            self.add(para['text'])
            end = len(self.sents)
            self.paras.extend([{
                'source': source,
                'page': page
            }] * (end-start))
            para['start'] = start
            para['end'] = end
        assert len(self.sents) == len(self.paras)
        doc['end'] = len(self.paras)
        self.docs[source] = doc

    def search(self, para, top_k=100, threshold=0.6):
        Vector, Text = encode(para)
        if not Vector.shape[0]: return []

        Score, Index = self.faiss_index.search(Vector, top_k)
        Result = []
        for i in range(Index.shape[0]):
            result = []
            for j in range(Index.shape[1]):
                if Index[i, j] < 0 or Score[i, j] < threshold: break
                result.append((Score[i, j], Index[i, j]))
            Result.append(result)
        return Result

    def search_doc(self, para, closely=0.05, nearly=0.001, **kwargs):
        Result = self.search(para, **kwargs)
        Docs = {}
        for result in Result:
            docs = {}
            for score, index in result:
                p = self.paras[index]
                source = p['source']
                if source not in docs:
                    docs[source] = {
                        'score': score,
                        'pages': set()
                    }
                if docs[source]['score']-score < closely:
                    docs[source]['pages'].add(p['page'])
            for source in docs:
                if source not in Docs:
                    Docs[source] = {
                        'score': 0.0,
                        'pages': set()
                    }
                Docs[source]['score'] += docs[source]['score']
                Docs[source]['pages'] |= docs[source]['pages']

        Result = [
            {
                'source': source,
                'score': Docs[source]['score'],
                'pages': Docs[source]['pages']
            }
            for source in Docs
        ]
        Result = sorted(Result, key=lambda x:x['score'], reverse=True)
        return filter(lambda x:Result[0]['score']-x['score'] < nearly, Result)

    def query(self, question, window_size=4, **kwargs):
        Result = list(self.search_doc(question, **kwargs))
        for result in Result:
            source = result['source']
            pages = sorted(list(result['pages']))
            paras = self.docs[source]['paras']
            left = 0
            for i in range(len(pages)):
                right = pages[i+1] if i+1 < len(pages) else len(paras)
                page = pages[i]
                for j in range(page-1, left, -1):
                    para = paras[j]
                    if 'text' not in para: break
                    if para['end']-para['start'] > 1: break
                    if page-j > window_size: break
                    result['pages'].add(j)
                for j in range(page, right):
                    result['pages'].add(j)
                    para = paras[j]
                    if 'text' not in para: break
                    if para['end']-para['start'] > 1: break
                    if j-page >= window_size: break
                left = j+1
        return Result

    def load(self):
        self.faiss_index = faiss.read_index(self.faiss_path+'/index.faiss')
        if faiss_gpu > 0: self.cpu_to_gpu()
        with open(self.faiss_path+'/index.sents', 'r', encoding='utf-8') as f:
            self.sents = json.load(f)
        with open(self.faiss_path+'/index.paras', 'r', encoding='utf-8') as f:
            self.paras = json.load(f)
        with open(self.faiss_path+'/index.docs', 'r', encoding='utf-8') as f:
            self.docs = json.load(f)

    def dump(self):
        if not os.path.exists(self.faiss_path): os.mkdir(self.faiss_path)
        if faiss_gpu > 0: self.gpu_to_cpu()
        faiss.write_index(self.faiss_index, self.faiss_path+'/index.faiss')
        if faiss_gpu > 0: self.cpu_to_gpu()
        with open(self.faiss_path+'/index.sents', 'w', encoding='utf-8') as f:
            json.dump(self.sents, f, ensure_ascii=False, indent=2)
        with open(self.faiss_path+'/index.paras', 'w', encoding='utf-8') as f:
            json.dump(self.paras, f, ensure_ascii=False, indent=2)
        with open(self.faiss_path+'/index.docs', 'w', encoding='utf-8') as f:
            json.dump(self.docs, f, ensure_ascii=False, indent=2)
