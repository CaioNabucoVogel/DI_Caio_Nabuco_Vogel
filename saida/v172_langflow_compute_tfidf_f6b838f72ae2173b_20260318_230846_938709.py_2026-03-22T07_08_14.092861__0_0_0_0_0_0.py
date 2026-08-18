def compute_tfidf(documents: list[str], query_terms: list[str]) -> list[float]:
    """Compute TF-IDF scores for query terms across a collection of documents.

    Args:
        documents: List of document strings
        query_terms: List of query terms to score

    Returns:
        List of TF-IDF scores for each document
    """
    tokenized_docs = [doc.lower().split() for doc in documents]
    n_docs = len(documents)
    document_frequencies = {}
    for term in query_terms:
        document_frequencies[term] = sum((1 for doc in tokenized_docs if term.lower() in doc))
    scores = []
    for doc_tokens in tokenized_docs:
        doc_score = 0.0
        doc_length = len(doc_tokens)
        term_counts = Counter(doc_tokens)
        for term in query_terms:
            term_lower = term.lower()
            tf = term_counts[term_lower] / doc_length if doc_length > 0 else 0
            idf = math.log(n_docs / document_frequencies[term]) if document_frequencies[term] > 0 else 0
            doc_score += tf * idf
        scores.append(doc_score)
    return scores