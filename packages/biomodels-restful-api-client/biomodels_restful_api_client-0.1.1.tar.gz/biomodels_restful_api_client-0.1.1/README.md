# BioModels RESTful Web Services

## Introduction
This package implements the **RESTful** API exposed in BioModels repository. All API endpoints can be followed up at 
[BioModels' RESTful Web Services](https://www.ebi.ac.uk/biomodels/docs/).

## Installation
```
pip install biomodels-restful-api-client
```

## Examples
### Fetch model metadata
```
>>> from biomodels_restful_api_client import services as bmservices
>>> bmservices.get_model_info("BIOMD0000000900")
{'name': 'Bianca2013 - Persistence analysis in a Kolmogorov-type model for cancer-immune system competition', ..., 
'submissionId': 'MODEL1912180002', 'publicationId': 'BIOMD0000000900'}
```

### Fetch model identifiers
```
>>> bmservices.get_model_identifiers()
{'hits': 2874, 'models': ['BIOMD0000000001', 'BIOMD0000000002', 'BIOMD0000000003', 'BIOMD0000000004', ...,
'MODEL9808533471', 'MODEL9810152478', 'MODEL9811206584']}
```

## Developers
* [Tung Nguyen](https://github.com/ntung)

## Contact
* [BioModels Developers](mailto:biomodels-developers@ebi.ac.uk)

## Licence
Please read [LICENSE](LICENSE) for information on the software availability and distribution.
