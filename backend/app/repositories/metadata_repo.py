from ..database  import neo4j_driver
from typing import Dict, Any

def execute_neo4j_query(query:str, params:Dict[str, Any]):
    with neo4j_driver.session() as session:
        result = session.run(query=query, parameters=params)
        print("QUERY: ", query)
        print("PARAMS: ", params)
        return result.data()