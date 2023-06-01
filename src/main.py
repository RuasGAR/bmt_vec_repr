# imports
from utils import read_config_file
from query_processor import *
from gli import read_xml_files, generate_records_csv
from index import generate_vec_space, save_vec_space
from search import search, ranking
import logging
import pickle


if __name__ == "__main__":

    # logging config
    logging.basicConfig(level=logging.DEBUG)

    # Loading all config files
    pc_config = read_config_file('pc.cfg')
    gli_config = read_config_file('gli.cfg',special_condition="gli")
    index_config = read_config_file('index.cfg')
    search_config = read_config_file('search.cfg')

    # PREPROCESS PHASE 
    logging.info("[PREPROCESS - START] query_processor.py starting...")

    queries_iterator = read_query_file(config=pc_config)
    queries = preprocessing_queries(queries_iterator,stem_flag=pc_config['STEMMER'])
    generate_query_csv(queries,config=pc_config)
    generate_expected_csv(queries_iterator,config=pc_config)
    
    logging.info("[PREPROCESS - END] query_processor.py has ended its activities.")
    

    # INVERTED LIST PHASE
    logging.info("[INVERTED LIST - START] gli.py starting...")

    data = read_xml_files(config=gli_config)
    generate_records_csv(config=gli_config)

    logging.info("[INVERTED LIST - END] gli.py ended.")

    # INDEXING PHASE
    logging.info("[INDEXING - START] index.py starting...")

    data,labels = generate_vec_space(config=index_config)
    save_vec_space(data,labels,dest="../../results")

    logging.info("[INDEXING - END] index.py ended.")  

    # SEARCHING PHASE
    model = {}
    
    logging.info("[SEARCH - START] search.py starting...")

    logging.info(f"Loading model in {search_config['MODELO']} ...")
    t_start = time.time()
    try:
        with open(search_config['MODELO'], 'rb') as f:
            model = pickle.load(f)
        t_end = time.time()
        logging.info(f"Loaded model successfully. (time elapsed: {(t_end-t_start):.5f} seconds)")
    except Exception as e:
        logging.exception("An error occurred while loading the model. Check further info below.")
        print(e)


    logging.info(f"Reading queries file located at {search_config['CONSULTAS']} ...")
    t_start = time.time()
    try:
        queries = pd.read_csv(search_config['CONSULTAS'], sep=";")
        t_end = time.time()
        logging.info(f"Read query file (containing {len(queries.index)} queries) successufully. (time elapsed:{(t_end-t_start):.5f} seconds)")
    except Exception as e:
        logging.exception("An error ocurred while reading the file. Check further info below.")
        print(e)

    # Applying necessary conversions
    string_to_list = lambda tokens: [t.strip() for t in tokens.split(",")]
    queries['QueryText'] = queries['QueryText'].apply(string_to_list)

    # Search module functionality        
    data = search(model,queries)
    ranking(data)

    # If already have intermediary results (therfore, non-ranked), use call below
    #ranking(None,True,'../../results/results[NON-RANKED].csv')
    
    logging.info("[SEARCH - END] search.py starting...")
