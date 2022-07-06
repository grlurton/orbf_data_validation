# Developing and benchmarking Risk Based Verification algorithms for RBF programs
===========================================================

## Project description

This project is part of [Bluesquare](https://bluesquarehub.com/)'s efforts to provide innovative solutions to mobilise and use health data to improve the organisation and delivery of health care in developing countries.

In most  Results Based Funding programs, facilities submit monthly reports to the financing entity. These reports are then verified by on site supervisions, and payments are made on the verified data. This verification ensures the payments made are based on tracable data, and thus offers incentives to improve data quality in health facilities. It is nonetheless costly to implement as verifications have to be performed every month in every facilities .

In order to reduce verification costs while still mitigating risks of over and under payments, we work on developing a set of algorithms, usable by RBF programs. This project aimed at defining and testing algorithms to orient program managers willing to only verify subsets of the data reported before making payments.

## Project Dimensions

### Algorithms development

### Benchmarking

## Contacts

Grégoire Lurton, (twitter: grlurton)

## Repository organization

Running Project
------------

Raw data is placed under data/raw/orbf_benin.csv. The script src/data/make_dataset.py should build the data used for analysis. All notebooks should run smoothly from there.

Project Organization
------------

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