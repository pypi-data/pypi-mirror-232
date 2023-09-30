"""Test ARS et all."""
import json
import os
import httpx
import asyncio
import requests
import time
import logging
from copy import deepcopy

logging.basicConfig(filename="test_ars.log", level=logging.DEBUG)
# We really shouldn't be doing this, but just for now...
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


BASE_PATH = os.path.dirname(os.path.realpath(__file__))
NORMALIZER_URL = "https://nodenormalization-sri.renci.org/get_normalized_nodes"
env_spec = {
    'dev': 'ars-dev',
    'ci': 'ars.ci',
    'test': 'ars.test',
    'prod': 'ars-prod'
}

def canonize(curies):

    if not isinstance(curies,list):
        curies = [curies]
    j ={
        "curies":curies,
        "conflate":True
    }
    r = requests.post(NORMALIZER_URL,json.dumps(j))
    rj=r.json()
    return rj

def keys_exist(element, *keys):
    if not isinstance(element, dict):
        raise AttributeError("keys_exists() expects dict as first argument.")
    if len(keys) == 0:
        raise AttributeError("keys_exists() expects at least two arguments, one given.")

    _element = element
    for key in keys:
        try:
            _element = _element[key]
            if _element is None:
                return False
        except KeyError:
            return False
    return True


def get_safe(element, *keys):
    """
    :param element: JSON to be processed
    :param keys: list of keys in order to be traversed. e.g. "fields","data","message","results
    :return: the value of the terminal key if present or None if not
    """
    if element is None:
        return None
    _element = element
    for key in keys:
        try:
            _element = _element[key]
            if _element is None:
                return None
            if key == keys[-1]:
                return _element
        except KeyError:
            return None
    return None


def get_files(relativePath):
    logging.debug("get_files")
    files = []
    my_dir = BASE_PATH + relativePath
    for filename in os.listdir(my_dir):
        if filename != ".DS_Store":
            files.append(os.path.join(my_dir, filename))
    return files


def test_must_have_curie(ARS_URL, query_type, expected_output, input_curie, output_curie):
    print(f" +++ +++ CHECKING FOR {output_curie} that {query_type} the {input_curie } +++ +++")
    logging.debug("test_must_have_curie")
    report_cards = {}
    if query_type == 'treats(creative)':
        template_dir = BASE_PATH + "/templates"
        try:
            with open(template_dir+'/treats.json') as f:
                template = json.load(f)

                # Fill message template with CURIEs
                message = deepcopy(template)
                nodes = get_safe(message, "message", "query_graph", "nodes")
                for node_val in nodes.values():
                    if 'ids' in node_val:
                        node_val['ids'].append(input_curie)
        except Exception as e:
            print(e)
    report_card = must_contain_curie(message, output_curie, expected_output, ARS_URL)
    print(json.dumps(report_card, indent=4, sort_keys=True))
    filename = input_curie+'_'+query_type+'_'+output_curie
    report_cards[filename] = report_card

    return report_cards


def call_ars(payload,ARS_URL):
    url = ARS_URL+"submit"
    logging.debug("call_ars")
    response = requests.post(url, json=payload, timeout=60.0)
    response.raise_for_status()
    return response.json()


def must_contain_curie(message, output_curie, expected_output, ARS_URL):
    logging.debug("must_contain_curie")

    logging.debug("query= " + json.dumps(message, indent=4, sort_keys=True))
    children, pk = get_children(message, ARS_URL)
    report_card = {}
    report_card['parent_pk'] = str(pk)
    report_card['actors'] = {}
    for entry in children:
        agent = entry[0]
        child = entry[1]
        results = get_safe(child, "fields", "data", "message", "results")
        if results is not None and agent.startswith('ara-'):
            all_ids = []
            for res in results:

                norm_score = res['normalized_score']
                if norm_score is None:
                    norm_score=0
                for res_node, res_value in res["node_bindings"].items():
                    for val in res_value:
                        ids = str(val["id"])
                        all_ids_flat = [item for sublist in all_ids for item in sublist]
                        if ids not in all_ids_flat:
                            all_ids.append([ids,norm_score])

            #get the top_n result's ids
            res_sort = sorted(results, key=lambda x: x['normalized_score'], reverse=True)
            if expected_output == 'TopAnswer':
                n_perc_res = res_sort[0:int(len(res_sort) * (float(10) / 100))]
            elif expected_output == 'Acceptable':
                n_perc_res = res_sort[0:int(len(res_sort) * (float(50) / 100))]
            elif expected_output == 'BadButForgivable':
                n_perc_res = res_sort[int(len(res_sort) * (float(50) / 100)):]
            elif expected_output == 'NeverShow':
                n_perc_res = res_sort
            else:
                logging.error("you have indicated a wrong category for expected output")

            n_perc_ids=[]
            for res in n_perc_res:
                for res_value in res["node_bindings"].values():
                    for val in res_value:
                        ids=str(val["id"])
                        if ids not in n_perc_ids:
                            n_perc_ids.append(ids)

            for id_score_set in all_ids:
                if output_curie in id_score_set[0]:
                    norm_score = id_score_set[1]
                    report_card['actors'][agent] = {}
                    report_card['actors'][agent]['score'] = norm_score
                    if expected_output == 'TopAnswer':
                        if output_curie in n_perc_ids:
                            report_card['actors'][agent]['drug_report'] = 'pass'
                        else:
                            report_card['actors'][agent]['drug_report'] = 'fail'

                    elif expected_output == 'Acceptable':
                        if output_curie in n_perc_ids:
                            report_card['actors'][agent]['drug_report'] = 'pass'
                        else:
                            report_card['actors'][agent]['drug_report'] = 'fail'

                    elif expected_output == 'BadButForgivable':
                        if output_curie in n_perc_ids:
                            report_card['actors'][agent]['drug_report'] = 'pass'
                        else:
                            report_card['actors'][agent]['drug_report'] = 'fail'

                    elif expected_output == 'NeverShow':
                        if output_curie in n_perc_ids:
                            report_card['actors'][agent]['drug_report'] = 'fail'
                        else:
                            report_card['actors'][agent]['drug_report'] = 'pass'

    return report_card


def get_children(query, ARS_URL, timeout=None):
    logging.debug("get_children")
    children = []
    response = call_ars(query, ARS_URL)
    time.sleep(300)
    pk = response["pk"]
    logging.debug("parent_pk for query {}  is {} ".format(query, str(pk)))
    url = ARS_URL + "messages/" + pk + "?trace=y"
    if timeout is None:
        timeout = 60
    r = requests.get(url, timeout=300.0)
    data = r.json()
    for child in data["children"]:
        agent = child["actor"]["agent"]
        childPk = child["message"]
        logging.debug("---Checking child for " + agent + ", pk=" + pk)
        childData = get_child(childPk, ARS_URL)
        if childData is None:
            pass
        else:
            # append each child with its results
            children.append([agent, childData])
    return children, pk


def get_child(pk, ARS_URL, timeout=60):
    logging.debug("get_child(" + pk + ")")
    wait_time = 10  # amount of seconds to wait between checks for a Running query result
    url = ARS_URL + "messages/" + pk
    child_response = requests.get(url, timeout=10)
    data = child_response.json()
    status = get_safe(data, "fields", "status")
    result_count = get_safe(data, "fields", "result_count")
    if status is not None:
        if status == "Done" and result_count is not None:
            if  result_count > 0:
                logging.debug("get_child for " +pk+ "returned"+ str(result_count )+"results")
                return data
            elif result_count == 0:
                logging.debug("get_child for " +pk+ "returned 0 results")
                return None
        elif status == "Running":
            if timeout > 0:
                logging.debug(
                    "Query response is still running\n"
                    + "Wait time remaining is now "
                    + str(timeout)
                    + "\n"
                    + "What we have so far is: "
                    + json.dumps(data, indent=4, sort_keys=True)
                )
                time.sleep(wait_time)
                return  get_child(pk, ARS_URL, timeout - wait_time)
            else:
                logging.debug("even after timeout" +pk+ "is still Running") # sorry bud, time's up
                return None
        else:
            # status must be some manner of error
            logging.debug(
                "Error status found in get_child for "
                + pk
                + "\n"
                + "Status is "
                + status
                + "\n"
                + json.dumps(data, indent=4, sort_keys=True)
            )
            return None
    else:
        # Should I be throwing an exception here instead?
        logging.error("Status in get_child for " + pk + " was no retrievable")
        logging.error(json.dumps(data, indent=4, sort_keys=True))
    # We shouldn't get here
    logging.error("Error in get_child for \n" + pk + "\n No child retrievable")
    return None


def run_semantic_test(env, query_type, expected_output, input_curie, output_curie):
    
    ars_env = env_spec[env]
    ARS_URL = f'https://{ars_env}.transltr.io/ars/api/'
    #get the report cards
    report_cards = test_must_have_curie(ARS_URL, query_type, expected_output, input_curie, output_curie)

    return report_cards


