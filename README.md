# Intelligent Data Quality Control Framework - A Case Study

An extensible Python framework for performing intelligent and rule-based data quality checks on structured 
datasets. This framework helps validate field formats, enforce data standards, and highlight issues 
before downstream processes.

## Project Structure
```text
ABN-INTERVIEW/
├── src/
│   ├── __init__.py
│   ├── data_preprocess/
│   │   ├── __init__.py
│   │   └── preclean_and_explore.py
│   ├── quality_checks/
│   │   ├── __init__.py
│   │   ├── data_quality_base.py
│   │   ├── validation_check.py
│   │   ├── basic_check.py
│   │   ├── advanced_check.py
│   │   └── ml_model_check.py
│   └── llm_assistance/
│       ├── __init__.py
│       └── llm_insight_generator.py
├── dev/
│   ├── input/
│   ├── output/
│   └── solution.ipynb
├── tests/
│   └── test_validation_check.py
├── requirements.txt
├── README.md
```

## Key Features
- **Data Understanding & Preparation**  
  Functions for initial data exploration, cleaning, and identifying key variables and growing markets.

- **Data Quality Checks**  
  - *Validation Checks*: Format validations for market exchange codes and ISO 4217 currency codes.  
  - *Basic Checks*: Detection of negative values, incorrect data types, string length issues, and missing values.  
  - *Advanced Checks*: Outlier detection using statistical methods and correlation analysis.  
  - *Machine Learning Checks*: Anomaly detection and predictive validation models applied to specific columns.

- **LLM-Assisted Explainability**  
  Integrates Large Language Models (LLMs) to translate technical and numerical results into clear, actionable
   insights for regulatory and business stakeholders.

- **Framework Design**  
  Built with scalability, maintainability, and pipeline monitoring in mind to ensure ongoing data correctness and
   quality assurance.

## Environment Setup

Follow these steps to set up your development environment:

### Step 1: Create a new conda environment

```bash
conda create -n abn_case python=3.12
conda activate abn_case
```

### Step 2: Install required packages

```bash
pip install -r requirements.txt
```

## Run Tests

Currently, the tests folder only contains one test script. This is to show we could put test scripts here
for unit testing of the functions in this repo. You could run tests using codes below:
```bash
python -m pytest tests
```

## Solution of the Case

Under dev folder, there is a notebook called solution.ipynb. In this notebook, it showcases how to
use this framework to check data qualities. 

Note: in order to use the LLM assistance, please input the api_key as an environment variable. 

