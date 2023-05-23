import pandas as pd
import logging
import time
import xml.etree.ElementTree as ET


logging.basicConfig(level=logging.DEBUG)
logging.info("[FILE] gli.py starting...")

def extract_path(string):
    return string.split("=")[1].replace("\n","")


# reading config
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

## READING FILES

def read_xml_files():
    
    logging.info("[FUNCTION] read_xml_files starting ...")

    filepaths_list = config["LEIA"]    
    logging.info(f"Found {len(filepaths_list)} 'LEIA'-oriented files.")

    acc = 0 
    el_iters = []
    t_start = time.time()
    for path in filepaths_list:

        logging.info(f"Reading: {path}...")
    
        with open(path) as f:
            try: 
                file_content = ET.parse(f);
                file_records = file_content.getroot().findall("RECORD")
                el_iters.append(file_records)
                acc += len(file_records)
                logging.info(f"Parsed {path} succesfully!")
            except Exception as e:
                logging.exception("Error while parsing the file content.")
                print(e);    

    t_end = time.time()
    
    logging.info(f"Read {len(el_iters)} XML files, with {acc} aggregated records, in {(t_end-t_start):.5f}s.")

    logging.info("[FUNCTION] read_xml_files end.")

    return el_iters # important to notice that this is already a iter through queries!!!

test = read_xml_files()