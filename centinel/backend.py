import os
import glob
import requests
import logging

import config

def request(slug):
    url = "%s/%s" % (config.server_url, slug)
    req = requests.get(url)

    req.raise_for_status()
    return req.json()

def get_recommended_version():
    return int(request("version")["version"])

def get_experiments():
    return request("experiments")["experiments"]

def get_results():
    return request("results")

def get_clients():
    return request("clients")

def submit_result(file_name):
    logging.info("Uploading result file - %s", file_name)

    with open(file_name) as result_file:
        file = {'result' : result_file}
        url = "%s%s" % (config.server_url, "/results")
        req = requests.post(url, files=file)

    req.raise_for_status()

def download_experiment(name):
    logging.info("Downloading experiment - %s", name)

    url = "%s/%s/%s" % (config.server_url, "experiments", name)
    req = requests.get(url)

def sync():
    logging.info("Starting sync with %s", config.server_url)

    # send all results
    # XXX: delete all files after sync?
    for path in glob.glob(os.path.join(config.results_dir,'[!_]*.json')):
        try:
            submit_result(path)
        except Exception, e:
            logging.error("Unable to send result file %s" % (path))

    # get all experiment names
    available_experiments = []
    for path in glob.glob(os.path.join(config.experiments_dir,'[!_]*.py')):
        file_name, _ = os.path.splitext(os.path.basename(path))
        available_experiments.append(file_name)
    available_experiments = set(available_experiments)

    # download new experiments from server
    for experiment in get_experiments():
        if experiment not in available_experiments:
            download_experiment(file_name)

    logging.info("Finished sync with %s", config.server_url)