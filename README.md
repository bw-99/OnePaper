## Install & Run GROBOID Docker Container
1. docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:${latest_grobid_version}

## Install scipdf parser librarary
1. pip install git+https://github.com/titipata/scipdf_parser
2. python -m spacy download en_core_web_sm

## Data Preperation
1. Run `python util/arxiv.py` to fetch relavant research papers and corresponding meta-data from arxiv.org
2. Run `python util/parse.py` to download the whole paper and parse the paper