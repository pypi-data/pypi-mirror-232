import os
import pathlib
import sys

from src.biomodels_restful_api_client import services as bmservices
import xml.etree.ElementTree as ET

"""
MODEL RELATED OPERATIONS
"""


def test_get_model_info():
    model_id = "BIOMD0000000500"
    out_format = "json"
    json = bmservices.get_model_info(model_id, out_format)
    actual_model_name = "Begitt2014 - STAT1 cooperative DNA binding - single GAS polymer model"
    assert actual_model_name == json["name"]
    actual_model_format = "SBML"
    assert actual_model_format == json["format"]["name"]

    # out_format = "xml"
    # xml = bmservices.get_model_info(model_id, out_format)
    # actual_model_name = "Begitt2014 - STAT1 cooperative DNA binding - single GAS polymer model"
    # assert actual_model_name == xml["name"]
    # actual_model_format = "SBML"
    # assert actual_model_format == xml["format"]["name"]


def test_get_model_files_info():
    model_id = "BIOMD0000000500"
    out_format = "json"
    json = bmservices.get_model_files_info(model_id, out_format)
    actual_main_file_name = "BIOMD0000000500_url.xml"
    actual_main_file_size = "83955"
    assert json["main"][0]["name"] == actual_main_file_name
    assert json["main"][0]["fileSize"] == actual_main_file_size


def test_get_model_identifiers():
    json = bmservices.get_model_identifiers()
    model_ids = json["models"]
    assert "BIOMD0000000500" in model_ids


def test_download():
    model_id = "BIOMD0000000500"
    main_file_name = "BIOMD0000000500_url.xml"

    download_file_path = bmservices.download(model_id, main_file_name)

    actual_download_file_name = os.path.basename(download_file_path).split('/')[-1]

    assert actual_download_file_name == main_file_name

    os.remove(download_file_path)


"""
MODEL SEARCH OPERATIONS
"""


def test_search():
    query = "MAPK"
    results = bmservices.search(query, num_results=20)
    assert results is not None
    assert len(results["models"]) == 20


"""
PARAMETERS SEARCH
"""


def test_parameter_search():
    query = "Cyclin"
    results = bmservices.parameter_search(query)
    assert results is not None
    assert len(results["entries"]) == 10
