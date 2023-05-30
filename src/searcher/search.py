import logging
import time
import pickle
import numpy as np
import pandas as pd
from configobj import ConfigObj



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


def search(model, queries):
    
    for q in queries:
        for token in q:
            pass
            
    

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

    queries = pd.read_csv(config['CONSULTAS'], sep=";")
