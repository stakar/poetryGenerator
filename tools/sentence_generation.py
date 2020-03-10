
        
class sentenceModel(object):
    
    def __init__(self):
        self = self
        
    def tokenize(self,lines):
        # integer encode sequences of words
        self.tokenizer = Tokenizer()
        self.tokenizer.fit_on_texts(lines)
        self.sequences = self.tokenizer.texts_to_sequences(lines)
        # vocabulary size
        self.vocab_size = len(self.tokenizer.word_index) + 1
        
    def prepare_dataset(self,filename,fileout):
        """Separate into input and output"""
        
        dC = documentCleaner(filename)
        dC.run(fileout)   
        
        self.tokenize(dC.sequences)
        
        sequences = array(self.sequences)
        
        self.X, self.y = sequences[:,:-1], sequences[:,-1]
        self.y = to_categorical(self.y, 
                                num_classes=self.vocab_size)
        self.seq_length = self.X.shape[1]
    
    def create_model(self):
        # define model
        model = Sequential()
        model.add(Embedding(self.vocab_size, 50, input_length=self.seq_length))
        model.add(LSTM(100, return_sequences=True))
        model.add(LSTM(100))
        model.add(Dense(100, activation='relu'))
        model.add(Dense(self.vocab_size, activation='softmax'))
        self.model = model
        print(model.summary())
        
    def compile_model(self,n_epoch=10):
        # compile model
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        # fit model
        self.model.fit(self.X, self.y, batch_size=128, epochs=n_epoch)

        # save the model to file
        self.model.save('model.h5')
        # save the tokenizer
        dump(self.tokenizer, open('tokenizer.pkl', 'wb'))
    
 
    # load doc into memory
    def load_doc(self,filename):
        # open the file as read only
        with open(filename, 'r',encoding='utf-8') as file:
            self.doc = file.read()

    @staticmethod
    def generate_seq(model, tokenizer, seq_length, seed_text, n_words):
        """Generate a sequence from a language model"""
        result = list()
        in_text = seed_text
        # generate a fixed number of words
        for _ in range(n_words):
            # encode the text as integer
            encoded = tokenizer.texts_to_sequences([in_text])[0]
            # truncate sequences to a fixed length
            encoded = pad_sequences([encoded], maxlen=seq_length, truncating='pre')
            # predict probabilities for each word
            yhat = model.predict_classes(encoded, verbose=0)
            # map predicted word index to word
            out_word = ''
            for word, index in tokenizer.word_index.items():
                if index == yhat:
                    out_word = word
                    break
            # append to input
            in_text += ' ' + out_word
            result.append(out_word)
        return ' '.join(result)
    
    def load_model(self,model_filename,tokenizer_filename):

        # load the model
        self.model = load_model(model_filename)

        # load the tokenizer
        self.tokenizer = load(open(tokenizer_filename, 'rb'))

    def generate(self,data_filename,n_words=50):
        self.load_doc(data_filename)
        lines = self.doc.split('\n')
        print(lines[0])
        self.seq_length = len(lines[0].split()) - 1
        
        
        seed_text = lines[randint(0,len(lines)-1)]
        
        generated = self.generate_seq(self.model,
                                      self.tokenizer,
                                      self.seq_length, 
                                      seed_text,
                                      n_words)
        return generated
    
        


# sM = sentenceModel()
# sM.prepare_dataset('..\datasets\dataset_barok.txt','data_clean.txt')
# sM.create_model()
# sM.compile_model(n_epoch=1)
# sM.generate('data_clean.txt')