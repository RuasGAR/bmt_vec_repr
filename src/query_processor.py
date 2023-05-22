import configparser
import pandas as pd
import xml.etree.ElementTree as ET
from unidecode import unidecode
import logging
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
import string
import time



# configs do logging
logging.basicConfig(level=logging.DEBUG)
logging.info("[FILE] query_processor.py starting...")

# leitura de configurações
config = configparser.ConfigParser();
try: 
    config.read("pc.cfg");
    logging.info("The config file was parsed with no errors.")
except Exception as e:
    logging.exception("Errors ocurred while parsing the config file.");
    print("For more information, check the exact error below:")
    print(e)




def read_query_file():
    logging.info("[FUNCTION] read_query_file starting ...")
    logging.info("Reading the file specified by the field 'LEIA'")
    filepath = config["QUERY_CONFIG"]["LEIA"];
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

    return file_content # important to notice that this is already a iter through queries!!!


def preprocessing_queries(et) -> pd.DataFrame:
    
    logging.info("[FUNCTION] preprocessing_queries starting ...")
    lang = 'english'
    
    # DataFrame
    cols = ["QueryNumber", "QueryText"]
    queries = pd.DataFrame(columns=cols)
    
    logging.info("Starting queries' preprocessing iteration...")
    t_start = time.time()
    for index,q in enumerate(et):
        q_num = int(q.find("QueryNumber").text)
        q_txt = q.find("QueryText").text.upper()
        q_txt = unidecode(q_txt)
        q_tokens = word_tokenize(q_txt, language=lang)
        # list comprehension to clean punctuation and stopwords
        q_tokens = [t for t in q_tokens if t not in string.punctuation and t not in stopwords.words(lang)]
        q = ','.join(q_tokens)
        queries.loc[index+1] = [q_num, q]
    t_end = time.time()
    logging.info(f"End of preprocessing after {(t_end-t_start):.5f}s")
    logging.info("[FUNCTION] preprocessing_queries ended")

    return queries


def generate_query_csv(queries):
    
    logging.info("[FUNCTION] generate_query_csv startig ...")
    filepath = config["QUERY_CONFIG"]["CONSULTAS"]
    
    try:
        queries.to_csv(filepath,sep=';',index=False) #overwrite as standard behaviour
    except Exception as e:
        logging.exception("Error while trying to create csv on {filepath}. More info below.")
        print(e);

        
def main():

    queries_iterator = read_query_file()
    queries = preprocessing_queries(queries_iterator)
    generate_query_csv(queries)


    
main()

logging.info("[FILE-DONE] query_processor.py has ended its activities.")
