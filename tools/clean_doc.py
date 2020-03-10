from numpy import array
from pickle import dump
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Embedding
import string
from random import randint
from pickle import load
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
 

class documentCleaner(object):
    
    def __init__(self,filename):
        self = self
        self.raw_text = self.load_doc(filename)
        self.filename = filename
    
    def load_doc(self,filename):
        """ Load document """
        with open(filename,'r',encoding='utf-8') as file:
            text = file.read()
        return text
    
    def clean_doc(delf,doc):
        """ Turn document into tokens """
        # replace '--' with a space ' '
        doc = doc.replace('--', ' ')
        # split into tokens by white space
        tokens = doc.split()
        # remove punctuation from each token
        table = str.maketrans('', '', string.punctuation)
        tokens = [w.translate(table) for w in tokens]
        # remove remaining tokens that are not alphabetic
        tokens = [word for word in tokens if word.isalpha()]
        # make lower case
        tokens = [word.lower() for word in tokens]
        return tokens
    
    @staticmethod
    def save_doc(lines,filename):
        data = '\n'.join(lines)
        with open(filename,'w',encoding='utf-8') as file:
            file.write(data)
            
    def run(self,outname):
        
        doc =  self.raw_text
        print(doc[:200])
        
        tokens = self.clean_doc(doc)

        print(tokens[:200])
        print('Total Tokens: %d' % len(tokens))
        print('Unique Tokens: %d' % len(set(tokens)))
 
        # organize into sequences of tokens
        length = 50 + 1
        sequences = list()
        for i in range(length, len(tokens)):
            # select sequence of tokens
            seq = tokens[i-length:i]
            # convert into a line
            line = ' '.join(seq)
            # store
            sequences.append(line)
        print('Total Sequences: %d' % len(sequences))
        self.sequences = sequences
        # save sequences to file
        
        self.outname = outname
        self.save_doc(sequences, self.outname)
        
        print('Saving as {}'.format(self.outname))



# dC = documentCleaner('..\datasets\dataset_barok.txt')
# dC.run('dataset_clean.txt')
