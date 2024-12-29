## GraphRAG Developments

### Docker Prep
1. cd to workspace
2. `docker pull bb1702/onepiece:main`
3. `docker run -dit --name con --shm-size=20g -v .:/workspace bb1702/onepiece:main`
4. `docker attach con`

### Run GraphRAG
1. Enter the container via `docker attach con`
2. `python3 -m graphrag ${command}` [command](https://microsoft.github.io/graphrag/get_started/)
   1. ex) `python3 -m graphrag init --root ./ragtest`

### Dev dependency
1. Install pre-commit on your dev environment (not docker, terminal you choose to use `git commit`) via `pip install pre-commit`


## Data Preperations

### Install & Run GROBOID Docker Container
1. docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:${latest_grobid_version}

### Install scipdf parser librarary
1. pip install git+https://github.com/titipata/scipdf_parser
2. python -m spacy download en_core_web_sm

### Scripts
1. Run `python util/arxiv.py` to fetch relavant research papers and corresponding meta-data from arxiv.org
2. Run `python util/parse.py` to download the whole paper and parse the paper

