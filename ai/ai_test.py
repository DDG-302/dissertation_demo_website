import json

from ai.tfidf.tfidf import TFIDF

dataset_path = "data/dataset_test.json"

data:dict
similar_question_list:list[list[str]] = []
ans_list:list[str] = []
with open(dataset_path, "r", encoding="utf8") as f:
    data = json.load(f)
    corpus = []
    for item in data["data"]:
        ans_list.append(item["answer"])
        similar_question_list.append(item["question"])

corpus = []
for item in data["data"]:
    doc = ""
    for q in item["question"]:
        doc += q + "\n" + item["answer"] + "\n"
    corpus.append(doc)


tfidf = TFIDF(corpus)

def get_ans(question:str, top_k:int=3, threshold:float=0.1, ignore_threshold:float=True):
    idx, val = tfidf.get_most_similar_doc_by_word(question, top_k=top_k)
    rtn_question = []
    rtn_ans = []
    rtn_tfidf = []
    for i, v in zip(idx, val):
        rtn_tfidf.append(v)
        if v >= threshold or ignore_threshold:
            similar_question = []
            for simq in similar_question_list[i]:
                similar_question.append(simq)
            rtn_question.append(similar_question)
            rtn_ans.append(ans_list[i])
        else:
            rtn_question.append([])
            rtn_ans.append("")
    return rtn_question, rtn_ans, rtn_tfidf
