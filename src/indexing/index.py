from math import log10
from configobj import ConfigObj
import pandas as pd
import logging
import numpy as np
import time
from scipy.sparse import csr_matrix
import pickle

# logging config
logging.basicConfig(level=logging.DEBUG)

"""  
    PONTOS CHAVE DE REFERÊNCIA

    - Cada elemento do vetor criado representa o termo no documento. 
    - Podemos utilizar o peso como semântica do elemento. 
    - O número de termos define as dimensões do espaço vetorial de um documento!
    - Tf-idf é interessante porque considera a relevância de um termo em um documento 
      comparado ao poder de idetificação de um termo. Basicamente a ideia é que se temos um 
      documento com um termo de alta incidência, mas que no corpus todo tem pouca aparição,
      a capacidade de caracterizar documentos do termo é maior (sempre pensando em referenciais)  
"""


# Config
config = {}
try: 
    config = ConfigObj('index.cfg')
    logging.info("The config file was parsed with no errors.")
except Exception as e:
    logging.exception("Errors ocurred while parsing the config file.");
    print("For more information, check the exact error below:")
    print(e)

# Main auxiliar methods
def tfn(doc_num,doc_list, tf_max):

    """ 
        Consider the example of a single line of the inverted list:

        FIBROSIS; [1,1,1,78,90,493,1202] 

        This function will compute the amount of times a DOCUMENT_NUMBER is repeated,
        which will give us the semantic value of the frequency of that term in that document.

        Then, this value is normalized using the frequency of the most frequent term.
    
    """

    return (doc_list.count(doc_num)/tf_max)


def idf(total_n, tf):
    return log10(total_n/tf)


def tf_idf(tf,idf):
    return tf*idf


def tf_max_all_docs(data,n_docs):
    """ Retorna um dicionário no formato a seguir: 

        {
            doc_number:
                [ 
                    number_of_terms (on the document) 
                    most_frequent_term, (on the document)
                    frequency_of_the_most_frequent_term (on the document)
                ]
        } 
    """

    logging.info("[FUNCTION] tf_max_all_docs starting ...")
    doc_info = {key: [0,"",0] for key in range(0,n_docs)}

    logging.info(f"Composing information of frequency for {n_docs} documents ...")
    t_start = time.time()

    for token,doc_list in data.itertuples(index=False):
        for d in doc_list:
            doc_info[d-1][0] += 1
            freq_of_t_in_d = doc_list.count(d)
            if freq_of_t_in_d > doc_info[d-1][2]:
                doc_info[d-1][1] = token
                doc_info[d-1][2] = freq_of_t_in_d
            

    t_end = time.time()
    logging.info(f"Finished collection in {(t_end-t_start):.5f}s.")
    logging.info("[FUNCTION] tf_max_all_docs ended.")

    return doc_info    



def weight(chosen_weight):
    # Abstraction to the metric used as weights
    # To add another option, you can extend this module with special functions and 
    # add its references below in a 'switch-case'-like structure

    if chosen_weight == 'tf-idf':
        return tf_idf
    else:
        return None


def generate_vec_space():
    """ 
        Gera uma matriz termo-documento, na qual os pesos estão representados com TF-IDF;
        dado o caminho do arquivo lido de index.cfg. 
    """
    
    logging.info("[FUNCTION] generate_vec_space starting ...")


    # reading data
    t_start = time.time()
    data = pd.read_csv(config['LEIA'],sep=";",converters={1:pd.eval})
    t_end = time.time()
    logging.info(f"Read inverted list data from {config['LEIA']} in {(t_end-t_start):.5f}s.")

    # IMPORTANT: we assume knowledge of how the inverted list is generated here.
    # Specifically: we are presuming that each term's document list is sorted.
    # With this assumption, we only check for the last element in each doc list to find the
    # greater value, which will be used as the total amount of documents. 
    n_docs = 0
    for i in range(len(data.index)):
        last_doc_on_item_i = data.iloc[i,-1][-1]
        if last_doc_on_item_i >= n_docs:
            n_docs = last_doc_on_item_i

    # matrix and labels-mapping dictionary
    matrix = np.zeros((len(data.index),n_docs))
    labels = {}

    doc_info = tf_max_all_docs(data, n_docs)    

    """ 
            Satisfying conditions:
            
                Instead of dealing with the terms' filter as given in the instructions by now,
                this module will assume that the following assertions were fulfilled while 
                creating the inverted list. 

                Then, all the terms have to:
                    - contain the minimum of 2 letters;
                    - use only letters, meaning that expressions containing numeric information
                    among standard letters (e.g. G6, AC-130, M0AB) are excluded;
                    - all terms are represented using A to Z (all capital letters) with 
                    ASCII code, removing expressions containing hifens and other symbolic forms;    
    """
    t_start = time.time()
    logging.info(f"Filling up term-document matrix with TF-IDF weights...")
    for index, row in enumerate(data.itertuples(index=False)):
        
        token, doc_list = row
        labels[token] = index

        for d in doc_list:
            d = int(d)
            if matrix[index][d-1] == 0:
                # Refer to the 'weight' function for explanation on the the applied logic
                tf_norm = tfn(d,doc_list,doc_info[d-1][2])
                inv_doc_freq = idf(n_docs,len(doc_list))
                matrix[index][d-1] = weight('tf-idf')(tf_norm, inv_doc_freq) 
            else:
                # if the value was already set, we don't need to re-calculate the weights
                continue
    t_end = time.time()
    logging.info(f"Term-document matrix ready. (time elapsed:{(t_end-t_start):.5f}s)")

    # converting the matrix to a sparse representation due to its density
    matrix = csr_matrix(matrix)

    logging.info("[FUNCTION] generate_vec_space ended.")

    return (matrix,labels)


def save_vec_space(sparse_matrix,labels,dest="../../generated"):
    try:
        logging.info(f"Saving given data into {dest} directory.")

        saveable = {'sparse_matrix':sparse_matrix, 'token':labels}
        with open(f'{dest}/vec_model.pkl','wb') as f:
            pickle.dump(saveable, f)    
        
        logging.info(f"Saved successfully to vec_model.pkl")
    except Exception as e:
        logging.exception("Error while saving the model (vectorial space). Check log below.")
        print(e)


if __name__ == "__main__":

    logging.info("[FILE] index.py starting...")
    data,labels = generate_vec_space()
    
    save_vec_space(data,labels)

    logging.info("[FILE] index.py ended.")
