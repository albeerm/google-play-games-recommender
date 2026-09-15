# Google Play Games Recommender

This project uses game descriptions and user ratings from the Google Play Store to create ranked game recommendations.

## What the project does

The project collects information about games and reviews from the Spanish Google Play Store. It processes the game descriptions and compares different ways of representing text, including Bag of Words, TF-IDF, Word2Vec, LDA, and BERT.

The processed data is then used to build content-based and collaborative recommendation models. The models recommend games based on either similar descriptions or patterns in user ratings.

## Main features

- Google Play Store data collection
- Text cleaning and preprocessing
- Spanish and English text processing with spaCy
- Exploratory data analysis
- Bag of Words and TF-IDF vectorization
- Word2Vec, LDA, and BERT models
- Content-based recommendations
- KNN and SVD collaborative filtering
- Neural collaborative filtering
- Comparison of different recommendation methods

## How it works

The game descriptions are cleaned by removing unnecessary words and keeping useful parts of the text. Different vectorization methods convert each description into numerical features that a machine learning model can compare.

For content-based recommendations, cosine similarity is used to find games with similar descriptions. The collaborative filtering models use patterns in user ratings to predict which games a user may like. We also tested a hybrid neural model that combines rating information with BERT description embeddings.

The final dataset contained 536 games and 13,837 ratings. The repository includes smaller samples of the game data, while the reviewer interaction data is not published for privacy.

## Technologies used

- Python
- Jupyter Notebook
- Pandas and NumPy
- Scikit-learn
- spaCy
- Gensim
- BERT / Sentence Transformers
- PyTorch
- KNN and SVD
- Natural language processing
- Machine learning

## Source code

The main project notebooks are located in:

```text
notebooks/
```

The Google Play data collection script is located at `scripts/dataset_final.py`, and sample game data is included in `data/`.

## What I learned

This project helped me understand the full process of building a machine learning system, starting with collecting and cleaning data and ending with comparing recommendation models. I learned how different text representations can change recommendation results and how content-based filtering differs from collaborative filtering. I also got more experience working with Spanish text, handling unbalanced and sparse data, using larger models such as BERT, and organizing a multi-step project across several notebooks.
