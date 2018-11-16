from scipy import sparse
from scipy.sparse import hstack

import time
import threading
import os.path

import numpy as np
import pandas as pd
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Dropout
from keras.utils import np_utils, to_categorical
from keras.optimizers import SGD, Adam
from keras.callbacks import TensorBoard, EarlyStopping


import turbodbc
from pandas.core.categorical import Categorical, CategoricalDtype


from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.preprocessing import OneHotEncoder, LabelBinarizer, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib

np.random.seed(2323)


class LabelEncoder2(LabelEncoder):

    def fit_transform(self, y, *args, **kwargs):
        return super().fit_transform(y).reshape(-1, 1)

    def transform(self, y, *args, **kwargs):
        return super().transform(y).reshape(-1, 1)


    
def transform_df(df):
    df = df.fillna('')
    for i in ['Artikelgruppe','Lieferantennummer','Eigenmarkencode', 'Serie']:
        df[i] = df[i].astype('category')
    df['Marge'] = np.round((df['Verkaufspreis'] - df['Einkaufspreis']).fillna(0.0), 5)
    df['Marge%'] = np.round((df['Marge'] / df['Verkaufspreis']).fillna(0.0), 5)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    return df    
    

def get_query():
    with open("query.sql") as f:
        q = f.read()
    return q


def create_connection_string_turbo(server, database):
    options = turbodbc.make_options(prefer_unicode=True)
    constr = 'Driver={ODBC Driver 13 for SQL Server};Server=' + \
        server + ';Database=' + database + ';Trusted_Connection=yes;'
    con = turbodbc.connect(connection_string=constr, turbodbc_options=options)
    return con



def get_xy(df,
           transformer_text,
           transformer_supplier,
           transformer_pl,
           transformer_serie):
    numeric_cols = StandardScaler().fit_transform(df[['Verkaufspreis',
                                                      'Einkaufspreis',
                                                      'Marge', 'Marge%']])
    
    numeric_sparse = sparse.csr_matrix(numeric_cols)
    onehot_text = transformer_text.transform(df['Artikel Bezeichnung'])

    onehot_supplier = transformer_supplier.transform(df['Lieferantennummer'].cat.codes.values.reshape(-1, 1))
    onehot_pl = transformer_pl.transform(df['Eigenmarkencode'].cat.codes.values.reshape(-1, 1))
    onehot_serie = transformer_serie.transform(df['Serie'].cat.codes.values.reshape(-1, 1))
    
    X = hstack([onehot_text,
                onehot_supplier,
                onehot_pl,
                onehot_serie,
                numeric_sparse])

    y = df['Artikelgruppe'].cat.codes.values
    
    return X.tocsr(), y


# Keras network (simple architecture)
def get_model(input_shape, n_classes, lr=0.1):
    model = Sequential()
    model.add(Dense(1000, activation='relu', input_shape=input_shape, name="input_layer"))
    model.add(Dropout(0.4))
    model.add(Dense(1000, activation='relu', name="hidden_layer_1"))
    model.add(Dropout(0.3))
    model.add(Dense(1000, activation='relu', name="hidden_layer_2"))
    model.add(Dropout(0.2))
    model.add(Dense(1000, activation='relu', name="hidden_layer_3"))
    model.add(Dropout(0.1))
    model.add(Dense(1000, activation='relu', name="hidden_layer_4"))
    model.add(Dense(n_classes, activation='softmax', name="output_layer"))
    sgd = SGD(lr=lr, decay=1e-6, momentum=0.9, nesterov=True)
    #adam = Adam(lr=lr, beta_1=0.9, beta_2=0.999)
    model.compile(loss='categorical_crossentropy',
                  optimizer=sgd,
                  metrics=['accuracy'])
    return model



class threadsafe_iter:
    """Takes an iterator/generator and makes it thread-safe by
    serializing call to the `next` method of given iterator/generator.
    """
    def __init__(self, it):
        self.it = it
        self.lock = threading.Lock()

    def __iter__(self):
        return self
    
    def __next__(self):
        with self.lock:
            return self.it.__next__()
        
        
def threadsafe_generator(f):
    """A decorator that takes a generator function and makes it thread-safe.
    """
    def g(*a, **kw):
        return threadsafe_iter(f(*a, **kw))
    return g


@threadsafe_generator
def batch_generator(X, y, batch_size, shuffle=True):
    samples_per_epoch = X.shape[0]
    number_of_batches = np.ceil(samples_per_epoch/batch_size)
    counter=0
    shuffle_index = np.arange(np.shape(y)[0])
    if shuffle:
        np.random.shuffle(shuffle_index)
    X =  X[shuffle_index, :]
    y =  y[shuffle_index]
    while 1:
        index_batch = shuffle_index[batch_size*counter:batch_size*(counter+1)]
        X_batch = X[index_batch,:].todense()
        y_batch = y[index_batch]
        counter += 1
        yield ((np.array(X_batch),y_batch))
        if (counter < number_of_batches):
            np.random.shuffle(shuffle_index)
            counter=0


            
@threadsafe_generator           
def single_batch_generator(X, batch_size=100):
    n_row = X.shape[0] 
    n_batches = np.ceil(n_row / batch_size)
    counter = 0
    idx = 0
    while counter < n_row:
        idx = counter
        counter += batch_size
        yield(X[idx:min(idx+batch_size, n_row), ])            
            
