import pandas as pd
import logging
from configobj import ConfigObj
import time
import xml.etree.ElementTree as ET


logging.basicConfig(level=logging.DEBUG)
logging.info("[FILE] gli.py starting...")

# reading config
config = {}
try: 
    config = ConfigObj("gli.cfg",list_values=True);
    logging.info("The config file was parsed with no errors.")
except Exception as e:
    logging.exception("Errors ocurred while parsing the config file.");
    print("For more information, check the exact error below:")
    print(e)

## READING FILES

def read_xml_files():
    
    logging.info("[FUNCTION] read_xml_files starting ...")

    filepaths_list = config["GLI_CONFIG"]["LEIA"]    
    logging.info(f"Found {len(filepaths_list)} 'LEIA'-oriented files.")

    acc = 0 
    el_iters = []
    t_start = time.time()
    for path in filepaths_list:

        logging.info(f"Reading: {path}...")
    
        with open(path) as f:
            try: 
                file_content = ET.parse(f);
                file_iter = file_content.getroot().iter("RECORD")
                el_iters.append(file_iter)
                acc += len(file_iter)
                logging.info(f"Parsed {path} succesfully!")
            except Exception as e:
                logging.exception("Erro while parsing the file content.")
                print(e);    

    t_end = time.time()
    
    logging.info(f"Read {len(el_iters)} XML files, with {acc} aggregated records, in {(t_end-t_start):.5f}s.")

    logging.info("[FUNCTION] read_xml_files end.")

    return el_iters # important to notice that this is already a iter through queries!!!

#test = read_xml_files()