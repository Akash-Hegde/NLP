from nltk.corpus import wordnet
import spacy
import urllib
import json
from spacy.tokenizer import Tokenizer
from spacy.lang.en.examples import sentences


nlp = spacy.load('en_core_web_lg')

class BestSyn:

    def get_datamuse_syn_list(self):
        
        url = "https://api.datamuse.com/words?ml=" + self.word
        with urllib.request.urlopen(url) as url1:
            response = url1.read()
        
        json_data  = json.loads(response.decode('utf-8'))
        word_list = []
        for x in json_data:
            word_list.append(x['word'])
        return word_list
        
        
       

    def __init__(self, word):
        self.word = word
        self.best_score = 0.0
        self.best_choice = ""


    def pull(self):
        words_list = self.get_datamuse_syn_list()
        for syn_word in words_list:
            use_nltk = True
            try:
                nltk_raw_word = wordnet.synsets(self.word)[0]
                nltk_syn_word = wordnet.synsets(syn_word)[0]
            except:
                use_nltk = False
            
            spacy_raw_word = nlp(str(self.word.lower()))
            spacy_syn_word = nlp(str(syn_word.lower()))

            
            spacy_score = spacy_raw_word.similarity(spacy_syn_word)
            
            if (use_nltk == True):
                nltk_score = nltk_syn_word.wup_similarity(nltk_raw_word)
                if (nltk_score == None):
                    nltk_score = 0
                score = (nltk_score+spacy_score)/2
            else:
                score = spacy_score

                
            if (score > self.best_score):
                self.best_score = score
                self.best_choice = syn_word
        result = [self.best_score, self.best_choice]
        return result

    def __del__(self):
        self.word = False
        self.best_score = False
        self.best_choice = False

        
class TextRewrite:


    def __init__(self, sentence):
        self.sentence = sentence

    def work(self):
        """
        @var rewrite_types: Type of words that can rewrited 
        """
        rewrite_types = [u'NN', u'NNS', u'JJ', u'JJS',u'VB',u'VBD',u'RB',u'RBS']
        pos_tokenizer = nlp(str(self.sentence))
        words = []
        for token in pos_tokenizer:
            #print(token.pos_, token.text, token.tag_)
            if token.tag_ in rewrite_types:
                words.append(token.text)
        rewrited_sentence = self.sentence
        for word in words:
            word_syn = BestSyn(word).pull()[1]
            rewrited_sentence = rewrited_sentence.replace(word, word_syn)
        return rewrited_sentence

    def __del__(self):
        self.sentence = False
print('Enter input')
sentences = list(input())

for sentence in sentences:
    new_sentence = TextRewrite(sentence).work() 
    print(new_sentence)
