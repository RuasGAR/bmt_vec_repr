from configobj import ConfigObj
import pandas as pd
import logging
import numpy as np
import time
from scipy.sparse import csr_matrix

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

def idf(data,n_docs):
    """ Retorna um dicionário no formato {doc_number: number_of_terms} """

    logging.info("[FUNCTION] idf starting ...")
    inverse_document_frequency = {key: 0 for key in range(0,n_docs)}

    logging.info(f"Counting the number of terms in each of the {n_docs} documents.")
    t_start = time.time()

    for _,doc_list in data.itertuples(index=False):
        for _d in doc_list:
            inverse_document_frequency[_d-1] += 1

    t_end = time.time()
    logging.info(f"Finished term count in {(t_end-t_start):.5f}s.")
    logging.info("[FUNCTION] idf ended.")

    return inverse_document_frequency    

def tf_idf(tf,idf):
    return tf/idf

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

    # IMPORTANT: it is assumed that the last element of the last doc_list points the Total number of documents
    # This is true considering the mecanism of inverted list generation, but be aware of this, anyhow
    last_doc_list = data.iloc[:,-1][len(data.index)-1]
    n_docs = last_doc_list[len(last_doc_list)-1] 

    matrix = np.zeros((len(data.index),n_docs))
        
    inv_doc_freq = idf(data,n_docs)

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
        
        _, doc_list = row

        for d in doc_list:
            d = int(d)
            if matrix[index][d-1] == 0:
                # Refer to the 'weight' function for explanation on the the applied logic
                matrix[index][d-1] = weight('tf-idf')(doc_list.count(d),inv_doc_freq[d-1]) 
            else:
                # if the value was already set, we don't need to re-calculate the weights
                continue
    t_end = time.time()
    logging.info(f"Term-document matrix ready. (time elapsed:{(t_end-t_start):.5f}s)")

    # converting the matrix to a sparse representation due to its density
    matrix = csr_matrix(matrix)

    logging.info("[FUNCTION] generate_vec_space ended.")

    return matrix


if __name__ == "__main__":

    logging.info("[FILE] index.py starting...")
    data = generate_vec_space()
    logging.info("[FILE] index.py ended.")
