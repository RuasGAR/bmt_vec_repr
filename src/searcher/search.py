import logging
import time
import pickle
import numpy as np
import pandas as pd
from configobj import ConfigObj
from scipy.sparse import csr_matrix

MIN_THRESHOLD = 0.7071

# logging config
logging.basicConfig(level=logging.DEBUG)

# Config
config = {}
try: 
    config = ConfigObj('search.cfg')
    logging.info("The config file was parsed with no errors.")
except Exception as e:
    logging.exception("Errors ocurred while parsing the config file.");
    print("For more information, check the exact error below:")
    print(e)

def cosine_distance(x,y):
    num = np.dot(x,y)
    denum = np.linalg.norm(x)*np.linalg.norm(y)
    return num/denum



def search(model, queries):
    
    sparse_matrix, tk_map = model['sparse_matrix'],model['token']
    print(tk_map.keys())

    res_filename = config['RESULTADOS']
    #results = pd.DataFrame(columns=["QUERY_ID","RESPONSE"])
    no_rank_results = [] # will be filled by tuples

    for i,q in enumerate(queries,start=1):

        individual_term_weight = 1/(len(q))
        query_vector = np.zeros((sparse_matrix.shape[0],1))

        # filling the query vector with terms weights
        for token in q:
            query_vector[tk_map[token]] = individual_term_weight
        
        # check distance to every document on the database
        for n,document in sparse_matrix.T:
            cos_dist = cosine_distance(query_vector, document)
            
            # For each I query, save distance COS_DIST evaluated in relation to N document
            # if the distance criteria of less than 45 degrees is obtained.
            # Ranking will be done afterwards.
            if cos_dist >= MIN_THRESHOLD:
                no_rank_results.append((i,n,cos_dist))


        print("cheguei aqui")
    

if __name__ == "__main__":
    
    model_path = config['MODELO']

    model = {}
    
    try:
        logging.info(f"Loading model in {model_path} ...")
        t_start = time.time()
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        t_end = time.time()
        logging.info(f"Loaded model successfully. (time elapsed: {(t_end-t_start):.5f} seconds)")
    except Exception as e:
        logging.exception("An error occurred while loading the model. Check further info below.")
        print(e)


    # TO-DO: encapsulate with logging and try catch blocks
    queries = pd.read_csv(config['CONSULTAS'], sep=";")

    search(model,queries)
