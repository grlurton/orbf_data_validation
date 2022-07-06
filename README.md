# Results Based Verification algorithms
==============================

## Project description

This project started as a consultancy with the information systems startup [Bluesquare](https://bluesquarehub.com/). Bluesquare provides information systems solutions for health programs in developing countries. Their platform [OpenRBF 2.0](https://bluesquarehub.com/services/openrbf-2-0/) is aimed at collecting reports from Results Based Funding programs.

In most  Results Based Funding programs using OpenRBF, facilities submit monthly reports to the financing entity. These reports are then verified by on site supervisions, and payments are made on the verified data. The organisation of such systems is described in details in :

This full verification ensures the accuracy of the payments made, but is costly to implement. This project aimed at defining and testing algorithms to orient program managers willing to only verify subsets of the data reported each month.

## Project Content

### Algorithms development

### Demonstration

### Code

### Documentation

## Contacts

Grégoire Lurton, (twitter: grlurton)
Antoine Legrand
Matthieu Antony

## Repository organization

Running Project
------------

Raw data is placed under data/raw/orbf_benin.csv. The script src/data/make_dataset.py should build the data used for analysis. All notebooks should run smoothly from there.



Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- What you are currently reading
    ├── data               <- Not commited in Git. Contact Bluesquare to discuss access.
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The data that has been processed and ready for modeling
    │   └── raw            <- Original Data obtained from Bluesquare.
    │
    ├── docs               <- Documentation for the project
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter noteboks.
    |   ├── exploratory    <- Notebooks used for initial exploration of data.
    |   └── reporting      <- Notebooks for reporting and discussion of results.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    |   ├── alarm_classification <- Scripts for classification of the different types of alarms raised by monitoring algorithms
    │   ├── data_preparation     <- Scripts to prepare data
    |   |   ├── a1.clean_raw_data_orbf.py      <- Loading and cleaning of raw OpenRBF Data.
    |   |   ├── make_dataset.py                <- Generic script calling others
    │   │   └── XX.make_references.py          <- Making all color dictionaries, ordered lists, tarifs lists.
    │   │
    │   ├── monitoring_algorithms <- Scripts to turn raw data into structured data for monitoring
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    |   |   ├── facility_monitoring.py      <- Definitions of Facilities Objects
    |   |   ├── make_facilities.py          <- Script to change data into formatted Faclities objects
    |   |   ├── reports_monitoring.py       <- Definitions of Reports Objects
    |   |   ├── series_monitoring.py        <- Definition of Series Objects
    │   │   └── simulate_supervisions.py    <- Script calling Facilities objects and running supervision
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
