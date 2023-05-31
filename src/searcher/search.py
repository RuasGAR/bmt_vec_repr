import logging
import time
import pickle
import numpy as np
import pandas as pd
from configobj import ConfigObj
from scipy.sparse import csr_matrix
from os import path
from functools import reduce
from typing import Tuple,List

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
    if denum <= 0:
        return 0
    else:
        cos_dist = num/denum
        cos_dist_float = cos_dist[0]
    return cos_dist_float

def search(model, queries):

    logging.info("[FUNCTION] search starting ...")
    
    sparse_matrix, tk_map = model['sparse_matrix'],model['token']
    sparse_matrix = csr_matrix(sparse_matrix)
    matrix = np.array(sparse_matrix.toarray())

    no_rank_results = pd.DataFrame(columns=["QUERY_ID","RESPONSE"])

    logging.info(f"Beggining search in vectorial model with {matrix.shape} dimensions.")
    elapsed_times = []

    for (i,q) in queries.itertuples(index=False):

        t_start = time.time()
        individual_term_weight = 1/(len(q))
        query_vector = np.zeros((matrix.shape[0],1))

        # filling the query vector with terms weights
        for token in q:
            if token in tk_map:
                query_vector[tk_map[token]] = individual_term_weight
        
        # check distance to every document on the database
        for n,document in enumerate(matrix.T):

            cos_dist = cosine_distance(document,query_vector)
            
            # For each I query, save distance COS_DIST evaluated in relation to N document
            # if the distance criteria of less than 45 degrees is obtained.
            # Ranking will be done afterwards.
            no_rank_results.loc[len(no_rank_results.index)-1] = (i,(n,cos_dist))

        t_end = time.time()
        elapsed_times.append((t_end-t_start))
        
        # PROGRESS AND DEBUG LOGGINGS
        if(i%10 == 0):
            logging.info(f"#### {i} queries analyzed.")

    logging.info(f"Search completed. (All {len(queries)} processed).")
    total_elapsed = reduce(lambda acc,x: acc + x, elapsed_times, 0)
    logging.info(f"#### Mean search interval: {(total_elapsed/len(elapsed_times)):.5f} seconds.")
    logging.info(f"#### Total searches' elapsed time: {total_elapsed:.5f} seconds.")
    del elapsed_times

    # INTERMEDIARY FILE SAVING
    # This part exists given the error-prone gap between the search and its ranking  
    res_basename_parts = path.basename(config['RESULTADOS']).split('.') 
    proxy_filename = (
        path.dirname(config['RESULTADOS']) + 
        path.sep + 
        res_basename_parts[0] + 
        '[NON-RANKED]' + 
        '.' + 
        res_basename_parts[1]
    )    
    
    try:
        logging.info(f"Saving proxy file WITHOUT RANKING in {proxy_filename} ...")
        no_rank_results.to_csv(proxy_filename, sep=";", index=False)
        logging.info(f"Saved successfully.")
    except Exception as e:
        logging.exception("An error ocurred while saving file. Check further info below.")
        print(e)
    
    logging.info("[FUNCTION] search ended.")

    return no_rank_results

def ranking(results:List[Tuple[int,int,float]]):
    for i in results:
        print(i)



if __name__ == "__main__":
    
    model_path = config['MODELO']

    model = {}
    
    logging.info(f"Loading model in {model_path} ...")
    t_start = time.time()
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        t_end = time.time()
        logging.info(f"Loaded model successfully. (time elapsed: {(t_end-t_start):.5f} seconds)")
    except Exception as e:
        logging.exception("An error occurred while loading the model. Check further info below.")
        print(e)


    logging.info(f"Reading queries file located at {config['CONSULTAS']} ...")
    t_start = time.time()
    try:
        queries = pd.read_csv(config['CONSULTAS'], sep=";")
        t_end = time.time()
        logging.info(f"Read query file (containing {len(queries.index)} queries) successufully. (time elapsed:{(t_end-t_start):.5f} seconds)")
    except Exception as e:
        logging.exception("An error ocurred while reading the file. Check further info below.")
        print(e)

    # Applying necessary conversions
    string_to_list = lambda tokens: [t.strip() for t in tokens.split(",")]
    queries['QueryText'] = queries['QueryText'].apply(string_to_list)

    # Search module functionality        
    search(model,queries)
