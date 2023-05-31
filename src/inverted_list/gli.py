import pandas as pd
import logging
import time
import re
import xml.etree.ElementTree as ET
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from unidecode import unidecode

# REGEX GLOBAL CONSTANT (notice that is applies to lower case)
FIT_PATTERN = re.compile(r'^[a-z]+$')

# logging config
logging.basicConfig(level=logging.DEBUG)


def extract_path(string):
    return string.split("=")[1].replace("\n","")


# reading actual config file
config = {"LEIA":[], "ESCREVA":""}
try: 
    with open("gli.cfg") as f:
        for line in f.readlines():
            if "ESCREVA" in line:
                config["ESCREVA"] = extract_path(line)    
            else:
                config["LEIA"].append(extract_path(line))
    logging.info("The config file was parsed with no errors.")
except Exception as e:
    logging.exception("Errors ocurred while parsing the config file.");
    print("For more information, check the exact error below:")
    print(e)
    exit()

## READING FILES

def read_xml_files():
    
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

# Auxiliar method for properly filtering undesired word structures
def check_string(str):
    
    # check for word size
    if (len(str) < 2):
        return False

    # checking for ASCII symbols other than letters form a to z, lower case.
    # this automatically exclude "words" formed only by ints (e.g. '189') and floats (e.g. '2.41'); 
    # and also remove blank strings such as ' ' and ` ` patterns 
    if (bool(FIT_PATTERN.match(str)) == False):
        return False

    # we return True to evaluate the str parameter as a valid token    
    return True

def generate_records_csv(records):
    
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
        rec_text = unidecode(rec_text).lower()
        tokens = word_tokenize(rec_text)
        words = [
            token.upper() for token in tokens 
            if check_string(token) and 
            token not in stopwords.words() 
        ]
        
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


if __name__ == "__main__":

    logging.info("[FILE] gli.py starting...")

    data = read_xml_files()
    generate_records_csv(data)

    logging.info("[FILE] gli.py ended.")   
