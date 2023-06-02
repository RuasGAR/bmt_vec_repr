import logging
import time
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from os import path
from functools import reduce
from typing import Tuple,List,Union
from utils import edit_fname_according_to_stemmer
import ast



def cosine_distance(x,y):
    num = np.dot(x,y)
    denum = np.linalg.norm(x)*np.linalg.norm(y)
    if denum <= 0:
        return 0
    else:
        cos_dist = num/denum
        cos_dist_float = cos_dist[0]
    return cos_dist_float

def search(model, queries, config):

    """ Returns non-ranked results in a Dataframe """


    logging.info("[FUNCTION] search starting ...")
    
    sparse_matrix, tk_map = model['sparse_matrix'],model['token']
    # TO-DO: Maybe the following two lines can be discarded
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
    
    proxy_filename = edit_fname_according_to_stemmer(proxy_filename, config['STEMMER'])

    try:
        logging.info(f"Saving proxy file WITHOUT RANKING in {proxy_filename} ...")
        no_rank_results.to_csv(proxy_filename, sep=";", index=False)
        logging.info(f"Saved successfully.")
    except Exception as e:
        logging.exception("An error ocurred while saving file. Check further info below.")
        print(e)
    
    logging.info("[FUNCTION] search ended.")

    return no_rank_results

def ranking(config,data:Union[List[Tuple[int,int,float]],None]=None, proxy_flag=False, proxy_fname=None):

    """ Saves and return the final results, ordeded by query_id and properly ranked acoording to cosine similarity """

    logging.info("[FUNCTION] ranking starting ...")

    if proxy_flag == True:
        logging.info("Usage of proxy file selected.")
        try:
            logging.info(f"Usage of proxy file {proxy_fname} selected.")
            data = pd.read_csv(proxy_fname, sep=";", converters={1:ast.literal_eval})
            logging.info("Loaded file successfully.")
        except Exception as e:
            logging.exception("An error ocurred while reading the file. Check info below for further details.")
            print(e)
               
    queries = set(data['QUERY_ID'])
    columns=['QUERY_ID', 'RESPONSE']
    final_results = pd.DataFrame(columns=columns)

    logging.info("Starting rank processing.")
    t_avg = 0
    t_start = time.time()
    for i,q_id in enumerate(queries,start=1):

        t_query_start = time.time()
        docs_distances_to_q = data[data['QUERY_ID'] == q_id]['RESPONSE']
        sorted_distances_to_q = sorted(docs_distances_to_q, key=lambda x:x[1], reverse=True) 
        
        ranking = 1
        for res in sorted_distances_to_q:
            (n_doc,dist) = res
            sorted_distances_to_q[ranking-1] = (ranking, n_doc, dist)
            ranking += 1    

        sorted_q_df = pd.DataFrame({'QUERY_ID':q_id, 'RESPONSE':sorted_distances_to_q}, columns=columns)
        
        final_results = pd.concat([final_results, sorted_q_df], ignore_index=True)
        t_query_end = time.time()

        t_avg = (t_avg + (t_query_end-t_query_start)) / 2 
        # DEBUGGING AND PROGRESS EVALUATION
        if(i%10 == 0):
            logging.info(f"#### {i} queries ranked so far, with average time of {t_avg:.5f} seconds.")

    t_end = time.time()
    logging.info(f"All queries {len(queries)} successfully ranked. (time elapsed:{(t_end-t_start):.5f} seconds)")


    try:
        logging.info(f"Saving final results dataset to {config['RESULTADOS']}")
        final_results.to_csv(
            edit_fname_according_to_stemmer(config['RESULTADOS'], config['STEMMER']),
            sep=";",
            index=False
        )
        logging.info(f"Saved dataset successfully.")
    except Exception as e:
        logging.exception("An error ocurred while saving the file. Check info below for further details.")
        print(e)

    logging.info("[FUNCTION] ranking ended.")

    return final_results

   