from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import requests
from urllib.parse import urlparse, urlunparse
from sentence_transformers import SentenceTransformer
import re
from difflib import SequenceMatcher
from collections import defaultdict
from rapidfuzz import process, fuzz
from wordfreq import top_n_list

load_dotenv()

app = Flask(__name__)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
CORS(app)

@app.route("/")
def home():
    return "PulseIQ backend is running!"


# Load common English words once when the backend starts.
COMMON_WORDS = top_n_list("en", 20_000)


def correct_query(query):
    original_query = query.strip()
    corrected_words = []

    for word in original_query.split():
        # Keep short words unchanged.
        if len(word) < 4:
            corrected_words.append(word)
            continue

        # Preserve the original spelling if no safe match exists.
        matches = process.extract(
            word.lower(),
            COMMON_WORDS,
            scorer=fuzz.ratio,
            limit=5
        )

        if not matches:
            corrected_words.append(word)
            continue

        best_word, best_score, _ = matches[0]

        # Require a stronger match for longer words.
        threshold = 80 if len(word) < 8 else 75

        if best_score >= threshold:
            corrected_words.append(best_word)
        else:
            corrected_words.append(word)

    corrected_query = " ".join(corrected_words)

    return {
        "original_query": original_query,
        "corrected_query": corrected_query
    }

@app.route("/api/search")
def search():

    query = request.args.get("q", "").strip()

    if not query:
        return {"error": "Query parameter 'q' is required."}, 400

    # Correct spelling before fetching news.
    correction = correct_query(query)

    original_query = correction["original_query"]
    corrected_query = correction["corrected_query"]

    print("Original query:", original_query)
    print("Corrected query:", corrected_query)

    api_key = os.getenv("GNEWS_API_KEY")

    url = "https://gnews.io/api/v4/search"

    params = {
        "q": corrected_query,
        "apikey": api_key
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

    except requests.RequestException:
        return {"error": "Unable to connect to news service"}, 503

    if response.status_code != 200:
        return {"error": "Failed to fetch news"}, response.status_code

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "News service returned an invalid response"}, 502

    if not isinstance(data, dict):
        return {"error": "Unexpected response from news service"}, 502

    if not isinstance(data.get("articles"), list):
        return {"error": "Unexpected article data from news service"}, 502

    articles = []

    for article in data.get("articles", []):
        source = article.get("source") or {}

        articles.append({
            "title": article.get("title") or "",
            "description": article.get("description") or "",
            "url": article.get("url") or "",
            "image": article.get("image") or "",
            "publishedAt": article.get("publishedAt") or "",
            "source": source.get("name") or "Unknown"
        })



    title_vectorizer = TfidfVectorizer()
    description_vectorizer = TfidfVectorizer()

    
    # Remove empty titles and their corresponding articles.
    valid_articles = [
        article for article in articles
        if article.get("title")
        and article["title"].strip()
    ]

    articles = valid_articles

    titles = [article["title"] for article in articles]
    descriptions = [
        article.get("description") or ""
        for article in articles
    ]

    if not titles:
        return {
            "original_query": original_query,
            "corrected_query": corrected_query,
            "query_was_corrected": (
                original_query.lower() != corrected_query.lower()
            ),
            "articles": [],
            "duplicate_groups": [],
            "message": "No usable news articles found for this query."
        }, 200


    title_matrix = title_vectorizer.fit_transform(titles)

    try:
        description_matrix = description_vectorizer.fit_transform(descriptions)
        description_query_vector = description_vectorizer.transform(
            [corrected_query]
        )
        description_similarities = cosine_similarity(
            description_query_vector,
            description_matrix
        )[0]

    except ValueError:
        description_similarities = [0.0] * len(articles)

    title_query_vector = title_vectorizer.transform([corrected_query])


    title_similarities = cosine_similarity(
        title_query_vector,
        title_matrix
    )[0]

    for article, title_score, description_score in zip(
        articles,
        title_similarities,
        description_similarities
    ):
        article["title_score"] = float(title_score)
        article["description_score"] = float(description_score)

        article["relevance_score"] = float(
            0.7 * title_score +
            0.3 * description_score
        )

    article_texts = [
    f"{article['title']}. {article['description'] or ''}"
    for article in articles
    ]

    query_embedding = embedding_model.encode(
        [corrected_query],
        normalize_embeddings=True
    )

    article_embeddings = embedding_model.encode(
        article_texts,
        normalize_embeddings=True
    )

    semantic_scores = cosine_similarity(
        query_embedding,
        article_embeddings
    )[0]

    for article, semantic_score in zip(articles, semantic_scores):
        article["semantic_score"] = float(semantic_score)

        article["combined_score"] = float(
            0.5 * article["relevance_score"] +
            0.5 * semantic_score
        )


    articles.sort(
        key=lambda article: article["combined_score"],
        reverse=True
    )

    
    
    def normalize_title(title):
        title = (title or "").lower()
        title = re.sub(r"[^a-z0-9\s]", "", title)
        return " ".join(title.split())

    def normalize_url(url):
        if not url:
            return ""

        parsed = urlparse(url)

        # Ignore tracking parameters and URL fragments.
        return urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",
            "",
            ""
        ))


    
# Group likely duplicate articles using title and description similarity.

    duplicate_groups = []
    grouped_indices = set()

    for i in range(len(articles)):
        if i in grouped_indices:
            continue

        article_1 = articles[i]
        title_1 = normalize_title(article_1.get("title"))
        description_1 = normalize_title(
            article_1.get("description")
        )
        url_1 = normalize_url(article_1.get("url"))

        group = [article_1]
        grouped_indices.add(i)

        for j in range(i + 1, len(articles)):
            if j in grouped_indices:
                continue

            article_2 = articles[j]
            title_2 = normalize_title(article_2.get("title"))
            description_2 = normalize_title(
                article_2.get("description")
            )
            url_2 = normalize_url(article_2.get("url"))

            title_similarity = SequenceMatcher(
                None, title_1, title_2
            ).ratio()

            description_similarity = (
                SequenceMatcher(
                    None, description_1, description_2
                ).ratio()
                if description_1 and description_2
                else 0.0
            )

            same_url = bool(url_1) and url_1 == url_2
            exact_title = bool(title_1) and title_1 == title_2

            likely_duplicate = (
                same_url
                or exact_title
                or (
                    title_similarity >= 0.90
                    and description_similarity >= 0.85
                )
            )

            if likely_duplicate:
                group.append(article_2)
                grouped_indices.add(j)

        if len(group) > 1:
            duplicate_groups.append({
                "title": group[0].get("title"),
                "count": len(group),
                "articles": [
                    {
                        "title": article.get("title"),
                        "source": article.get("source"),
                        "url": article.get("url")
                    }
                    for article in group
                ]
            })

    print("Duplicate groups:", duplicate_groups)

    
    # Remove duplicate copies from the main articles list.
    duplicate_urls = {
        normalize_url(article.get("url"))
        for group in duplicate_groups
        for article in group["articles"][1:]
        if article.get("url")
    }

    articles = [
        article for article in articles
        if normalize_url(article.get("url")) not in duplicate_urls
    ]

    result = {
        "original_query": original_query,
        "corrected_query": corrected_query,
        "query_was_corrected": (
            original_query.lower() != corrected_query.lower()
        ),
        "articles": articles,
        "duplicate_groups": duplicate_groups
    }

    print("Corrected query:", corrected_query)
    return result



if __name__ == "__main__":
    app.run(debug=True)