# Google Play Games Recommender

This is a machine learning project I worked on with my group for our Machine Learning Applications course at UC3M. We built the dataset ourselves from the Spanish Google Play Store and compared different ways of recommending games.

The main goal was to take raw game descriptions and user ratings, process them, and turn them into ranked game recommendations.

## What the project does

- Collects game information and reviews with `google-play-scraper`
- Cleans Spanish and English text with spaCy
- Compares Bag of Words, TF-IDF, Word2Vec, LDA, and BERT representations
- Builds content-based recommendations using game-description similarity
- Tests collaborative filtering with KNN, SVD, and neural models
- Compares the different recommendation approaches and their results

## Dataset

The final dataset contains:

- 536 games across 44 genres
- 13,837 user-game ratings
- 1,548 users and 467 rated games in the interaction dataset

The data was collected from the Spanish Google Play Store. The game descriptions are mostly in Spanish, with some English words and phrases.

## Project files

```text
google-play-games-recommender/
├── data/                       # Raw and preprocessed CSV datasets
├── notebooks/
│   ├── 01_EDA_preprocessing.ipynb
│   ├── 02_vectorization_classical.ipynb
│   ├── 03_vectorization_w2v.ipynb
│   ├── 04_lda_topic_modeling.ipynb
│   ├── 05_bert_embeddings.ipynb
│   └── 06_recommender_system.ipynb
├── scripts/
│   └── dataset_final.py        # Google Play data collection script
└── requirements.txt
```

The notebooks are numbered in the order they should be viewed. Most of them already include their outputs, so the analysis and results can be seen directly on GitHub without rerunning the full pipeline.

## Main approaches

### Content-based filtering

Games are represented using their descriptions. Cosine similarity is then used to find games with similar content. We compared several text representations instead of relying on only one model.

### Collaborative filtering

The interaction dataset is used to recommend games based on rating patterns. We tested neighborhood-based KNN, SVD matrix factorization, neural collaborative filtering, and a hybrid model using BERT embeddings.

## Running the notebooks

Create a virtual environment and install the packages:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download es_core_news_md
python -m spacy download xx_sent_ud_sm
```

Then open Jupyter Notebook or JupyterLab and run the notebooks in numerical order. Some of the later notebooks can take a while because they train larger models such as BERT and neural recommenders.

## Project note

This was completed as a group project for our Machine Learning Applications course.
