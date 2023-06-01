import re
import logging
from os import path
from configobj import ConfigObj
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
nltk.download('punkt')
nltk.download('stopwords')

# Global instances
porter = PorterStemmer()
FIT_PATTERN = re.compile(r'^[a-z]+$')

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

def remove_stopwords_normalize_and_apply_stemmer(token_list,stemmer_flag=False):
    
    if(stemmer_flag == True):
    
        filtered_list = [porter.stem(t).upper() for t in token_list if (t not in stopwords.words("english") and check_string(t))] 

    else:
        filtered_list = [t.upper() for t in token_list if (t not in stopwords.words("english") and check_string(t))] 
    
    return filtered_list


def read_config_file(fname,special_condition):

    # Config
    config = {}
    try: 
        config = ConfigObj(fname)
        logging.info(f"The {fname} config file was parsed with no errors.")
    except Exception as e:
        logging.exception("Errors ocurred while parsing the config file.");
        print("For more information, check the exact error below:")
        print(e)

    if special_condition == "gli":
        config = {"LEIA":[], "ESCREVA":"", "STEMMER":0}
        try: 
            with open("gli.cfg") as f:
                for line in f.readlines():
                    if "ESCREVA" in line:
                        config["ESCREVA"] = extract_path(line)
                    elif "STEMMER" in line:
                        config['STEMMER'] = int(extract_path(line))    
                    else:
                        config["LEIA"].append(extract_path(line))
            logging.info("The config file was parsed with no errors.")
        except Exception as e:
            logging.exception("Errors ocurred while parsing the config file.");
            print("For more information, check the exact error below:")
            print(e)
            exit()

    return config


def extract_path(string):
    return string.split("=")[1].replace("\n","")

def edit_fname_according_to_stemmer(standard_fname,stemmer_flag):

    file_basename, extension = path.basename(standard_fname).split('.')
    dirs = path.dirname(standard_fname)

    stemmer = ""
    if bool(stemmer_flag) == True:
        stemmer = "STEMMER"
    else:
        stemmer = "NOSTEMMER"
        
    return (path.join(dirs,file_basename)+'-'+stemmer+'.'+extension) 
        