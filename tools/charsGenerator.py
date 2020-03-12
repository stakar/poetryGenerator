from __future__ import print_function
from keras.callbacks import LambdaCallback
from keras.models import Sequential,load_model
from keras.layers import Dense
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import io



class generateNetChars(object):
    
    def __init__(self,maxlen=40,step=3):
        self = self
        self.maxlen = maxlen
        self.step = 3
    
    def load_dataset(self,filename):
        with open(filename,'r',encoding='utf-8') as txt:
            text = txt.read()
        print('Document loaded\nCorpus length:', len(text))
        self.text = text

    def prep_data(self):
        
        self.chars = sorted(list(set(self.text)))
        print('total chars:', len(self.chars))
        self.char_indices = dict((c, i) for i, c in enumerate(self.chars))
        self.indices_char = dict((i, c) for i, c in enumerate(self.chars))
        
        print('Example chars: {}'.format(list(self.char_indices.keys())[:10]))
        print('Char indexes: {}'.format(list(self.char_indices.values())[:10]))
        
        self.sentences = []
        self.next_chars = []
        for i in range(0, len(self.text) - self.maxlen, self.step):
            self.sentences.append(self.text[i: i + self.maxlen])
            self.next_chars.append(self.text[i + self.maxlen])
        print('nb sequences:', len(self.sentences))
        
        self.x = np.zeros((len(self.sentences),self.maxlen,len(self.chars)), 
                           dtype=np.bool)
        self.y = np.zeros((len(self.sentences),
                           len(self.chars)), dtype=np.bool)
        for i, sentence in enumerate(self.sentences):
            for t, char in enumerate(sentence):
                self.x[i, t, self.char_indices[char]] = 1
            self.y[i, self.char_indices[self.next_chars[i]]] = 1
            
    def create_model(self):
        # build the model: a single LSTM
        print('Build model...')
        self.model = Sequential()
        self.model.add(LSTM(128, input_shape=(self.maxlen, len(self.chars))))
        self.model.add(Dense(len(self.chars), activation='softmax'))
        
    def compile_model(self,n_epochs,filename='model'):
        self.__optimizer = RMSprop(lr=0.01)
        
        self.__print_callback = LambdaCallback(on_epoch_end=self.on_epoch_end)
        self.model.compile(loss='categorical_crossentropy', optimizer=self.__optimizer)
        
        self.model.fit(self.x, self.y,
                       batch_size=128,
                       epochs=n_epochs,
                       callbacks=[self.__print_callback])
        self.model.save('{}.h5'.format(filename))
        self.model.save_weights('{}Weights.h5'.format(filename))
        
    @staticmethod
    def sample(preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    
    def on_epoch_end(self,epoch, _):
        # Function invoked at end of each epoch. Prints generated text.
        print()
        print('----- Generating text after Epoch: %d' % epoch)

        start_index = random.randint(0, len(self.text) - self.maxlen - 1)
        for diversity in [0.2, 0.5, 1.0, 1.2]:
            print('----- diversity:', diversity)

            generated = ''
            sentence = self.text[start_index: start_index + self.maxlen]
            generated += sentence
            print('----- Generating with seed: "' + sentence + '"')
            sys.stdout.write(generated)

            for i in range(400):
                x_pred = np.zeros((1, self.maxlen, len(self.chars)))
                for t, char in enumerate(sentence):
                    x_pred[0, t, self.char_indices[char]] = 1.

                preds = self.model.predict(x_pred, verbose=0)[0]
                next_index = self.sample(preds, diversity)
                next_char = self.indices_char[next_index]

                generated += next_char
                sentence = sentence[1:] + next_char

                sys.stdout.write(next_char)
                sys.stdout.flush()
            print()
            
    def load_prev_model(self,modelname):
        self.model = load_model(modelname)

    def generate(self,n_texts=10):
        
        neural_texts = list()
        for n in range(n_texts):
            start_index = random.randint(0, len(self.text) - self.maxlen - 1)
            for diversity in [0.2, 0.5, 1.0, 1.2]:
                print('----- diversity:', diversity)

                generated = ''
                sentence = self.text[start_index: start_index + self.maxlen]
                generated += sentence
                print('----- Generating with seed: "' + sentence + '"')
                sys.stdout.write(generated)

                for i in range(400):
                    x_pred = np.zeros((1, self.maxlen, len(self.chars)))
                    for t, char in enumerate(sentence):
                        x_pred[0, t, self.char_indices[char]] = 1.

                    preds = self.model.predict(x_pred, verbose=0)[0]
                    next_index = self.sample(preds, diversity)
                    next_char = self.indices_char[next_index]

                    generated += next_char
                    sentence = sentence[1:] + next_char

                    sys.stdout.write(next_char)
                    sys.stdout.flush()
                print()
            neural_texts.append({diversity:generated})
            
        return neural_texts