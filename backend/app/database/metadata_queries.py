from ..database  import neo4j_driver


# ajustarrr es una query random esta
def get_quality_results(collection_id: str, quality_id: str, limit: int):
    query = """
        MATCH (c:Collection)-[:HASQUALITY]->(q:Quality)
        WHERE c.id = $collection_id AND q.id = $quality_id
        RETURN q LIMIT $limit
    """
    params = {
        'collection_id': collection_id,
        'quality_id': quality_id,
        'limit' : limit
    }
    with neo4j_driver.session() as session:
        result = session.run(query=query, parameters=params)
        return result.data()