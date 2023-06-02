from unidecode import unidecode
import xml.etree.ElementTree as ET
import pandas as pd
import logging
from utils import remove_stopwords_normalize_and_apply_stemmer, edit_fname_according_to_stemmer
from nltk.tokenize import word_tokenize
import time


###### QUERY GENERATION

def read_query_file(config):
    logging.info("[FUNCTION] read_query_file starting ...")
    logging.info("Reading the file specified by the field 'LEIA'")
    filepath = config["LEIA"];
    logging.info(f"The file to be read is located/have name: {filepath}")
    
    with open(filepath) as f:
        logging.info("The program is about to parse the file content.")
        try: 
            file_content = ET.parse(f);
            file_content = file_content.getroot() # importante!!
            logging.info(f"Parsed {filepath} succesfully")
        except Exception as e:
            logging.exception("Erro while parsing the file content.")
            print(e);    

    count = 0
    for _ in file_content.iter("QUERY"):
        count += 1 
    logging.info(f"Read {count} queries.")
    logging.info("[FUNCTION] read_query_file end.")

    return file_content 


def preprocessing_queries(et,stem_flag) -> pd.DataFrame:
    
    logging.info("[FUNCTION] preprocessing_queries starting ...")
    lang = 'english'
    
    # DataFrame
    cols = ["QueryNumber", "QueryText"]
    queries = pd.DataFrame(columns=cols)
    
    logging.info("Starting queries' preprocessing iteration...")
    t_start = time.time()
    for index,q in enumerate(et):
        q_num = int(q.find("QueryNumber").text)
        q_txt = q.find("QueryText").text
        q_txt = unidecode(q_txt)
        q_tokens = word_tokenize(q_txt, language=lang)
        q_tokens = remove_stopwords_normalize_and_apply_stemmer(q_tokens, stem_flag)
        q = ','.join(q_tokens)
        queries.loc[index+1] = [q_num, q]
    t_end = time.time()
    logging.info(f"End of preprocessing after {(t_end-t_start):.5f}s")
    logging.info("[FUNCTION] preprocessing_queries ended")

    return queries


def generate_query_csv(queries,config):
    
    logging.info("[FUNCTION] generate_query_csv starting ...")
    filepath = edit_fname_according_to_stemmer(config["CONSULTAS"],config['STEMMER'])  
    
    
    try:
        queries.to_csv(filepath,sep=';',index=False) #overwrite as standard behaviour
    except Exception as e:
        logging.exception(f"Error while trying to create csv on {filepath}. More info below.")
        print(e);

    logging.info("[FUNCTION] generate_query_csv ended.")


##### EXPECTED generation

def generate_expected_csv(q_iter,config):

    logging.info("[FUNCTION] generate_expected_csv starting ...")
    cols = ["QueryNumber", "DocNumber", "DocVotes"]
    expected_data = pd.DataFrame(columns=cols)

    logging.info("Processing Documents and its Scores...")
    t_start = time.time()
    
    for row in q_iter:
        
        r_num = int(row.find("QueryNumber").text)

        for item in row.iter("Item"):
            doc_num = item.text
            doc_score = item.get('score').replace('0','')
            if doc_score: # condition just in case the replacement of zeros cause the field to be empty
                score = len(doc_score)
            expected_data.loc[len(expected_data)] = [r_num, doc_num, score]

    t_end = time.time()
    logging.info(f"Processed a total of {len(expected_data)-1} itens in {(t_end-t_start):.5f}s.")

    # saving to CSV file ...
    
    filepath = edit_fname_according_to_stemmer(config["ESPERADOS"],config['STEMMER'])

    try:
        logging.info("Creating expected results file according to 'ESPERADOS' config field.")
        expected_data.to_csv(filepath,sep=";",index=False)
    except Exception as e:
        logging.exception(f"Error ocurred while saving to {filepath}. See more details below.")
        print(e)

    logging.info("File created succesfully.")

    logging.info("[FUNCTION] generate_expected_csv ended.")



