import configparser
import pandas as pd
import xml.etree.ElementTree as ET
from unidecode import unidecode
import logging

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
    logging.info(f"Read {count} amount of queries.")

    return file_content





def generate_query_and_expected_csv(et):
    
    # Pegando campos de um consulta
    fields = [];
    for child in et.find("QUERY"):
        fields.append(child.tag);
    
    # Primeiro arquivo -> CONSULTAS
    queries = pd.DataFrame(columns=fields[:2]);
    for q in et.iter("QUERY"):
        queries["QueryNumber"] = int(q.find("QueryNumber").text)
    print(queries.head());

    prepared_queries_txt = preprocessing_pipeline(queries["QueryText"]); 

    # Segundo arquivo -> ESPERADOS
    #expected = pd.DataFrame(columns=[fields[0],"DocNumber","DocVotes"]);



    pass
    
def preprocessing_pipeline(text_batch):
    print(f"text {text_batch}");
    for q in text_batch:
        q = unidecode().upper()
        




test = read_query_file()    
#generate_query_and_expected_csv(test);

logging.info("[FILE-DONE] query_processor.py has ended its activities.")
