from gensim.models import Word2Vec

#news_model_loaded = KeyedVectors.load_word2vec_format('dblp_cbow_100_3000000.bin', binary=True)
news_model_loaded = Word2Vec.load('dblp_cbow_100.bin')
#print(news_model_loaded.most_similar(positive='tss'))
#print(news_model_loaded.most_similar(positive='time'))
#print(news_model_loaded.most_similar(positive='sharing'))
#print(news_model_loaded.wv.most_similar(positive='system'))
print([term for term, dist in news_model_loaded.wv.most_similar(positive='operating') if dist > 0.6])
print([term for term, dist in news_model_loaded.wv.most_similar(positive='system') if dist > 0.6])
print([term for term, dist in news_model_loaded.wv.most_similar(positive=['which','operating', 'system', 'is', 'best'], topn=3)])
#topn=4