import logging
import time
import xml.etree.ElementTree as ET
from nltk.tokenize import word_tokenize
from utils import remove_stopwords_normalize_and_apply_stemmer


## READING FILES

def read_xml_files(config):
    
    logging.info("[FUNCTION] read_xml_files starting ...")

    filepaths_list = config["LEIA"]    
    logging.info(f"Found {len(filepaths_list)} 'LEIA'-oriented files.")

    acc = 0 
    records = []
    t_start = time.time()
    for path in filepaths_list:

        logging.info(f"Reading: {path}...")
    
        with open(path) as f:
            try: 
                file_content = ET.parse(f);
                file_records = file_content.getroot().findall("RECORD")
                records += file_records
                acc += len(file_records)
                logging.info(f"Parsed {path} succesfully!")
            except Exception as e:
                logging.exception("Error while parsing the file content.")
                print(e)
                exit()

    t_end = time.time()
    
    logging.info(f"Read {len(filepaths_list)} XML files, with {acc} aggregated records, in {(t_end-t_start):.5f}s.")

    logging.info("[FUNCTION] read_xml_files end.")

    return records 



def generate_records_csv(records,config):
    
    logging.info("[FUNCTION] generate_records_csv starting ...")
    
    path = config["ESCREVA"]

    data = {}

    t_start = time.time()
    logging.info(f"Starting creation of Inverted List with {len(records)} documents.")

    counter = 0
    for rec in records:
        
        # Retrieving info
        rec_num = int(rec.find("RECORDNUM").text)
        rec_text = ""
        if rec.find("ABSTRACT") == None:
            if rec.find("EXTRACT") == None:
                continue
            else:
                rec_text = rec.find("EXTRACT").text
        else:
            rec_text = rec.find("ABSTRACT").text        
            
        # Normalizing and extracting stopwords
        rec_text = rec_text.lower()
        tokens = word_tokenize(rec_text)
        words = remove_stopwords_normalize_and_apply_stemmer(tokens, stemmer_flag=config['STEMMER'])
        
        # Data filling
        for w in words:
            if w not in data:
                data[w] = [rec_num]
            else:
                data[w].append(rec_num)

        # Progress information
        if(counter % 50 == 0 and counter != 0):
            logging.info(f"Processed {counter} documents (time elapsed:{(time.time())-t_start:.5f} seconds)")

        counter += 1
    
    t_end = time.time()
    logging.info(f"Inverted List successfully created with {len(data.keys())} words, in {(t_end-t_start):.5f}s.")

    logging.info(f"Saving index to csv file in the following path: {path}")
    try:
        with open(path,'w+') as f:
            for token in data.keys():
                f.write(f"{token};{data[token]}\n")
    except Exception as e:
        logging.exception('An error occurred while saving data to csv file.')
        print(e);
        exit()
    logging.info(f"File successfully created!")

    logging.info("[FUNCTION] generate_records_csv ended.")
