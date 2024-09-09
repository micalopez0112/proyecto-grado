

def get_hardcoded_test_documents():
    documents = [
        {
            "type": "Destination",
            "name": "Paris",
            "description": "The capital city of France, known for its art, fashion, and culture.",
            "iri": "http://www.owl-ontologies.com/travel.owl#Paris"
        },
        {
            "type": "Destination",
            "name": "New York",
            "description": "A major city in the United States, known for its skyscrapers and cultural diversity.",
            "iri": "http://www.owl-ontologies.com/travel.owl#NewYork"
        },
        {
            "type": "Adventure",
            "name": "Skydiving",
            "description": "An extreme sport that involves jumping from an aircraft and free-falling before deploying a parachute.",
            "iri": "http://www.owl-ontologies.com/travel.owl#Skydiving"
        },
        {
            "type": "Adventure",
            "name": "Scuba Diving",
            "description": "A mode of underwater diving where the diver uses a self-contained underwater breathing apparatus (scuba).",
            "iri": "http://www.owl-ontologies.com/travel.owl#ScubaDiving"
        },
        {
            "type": "Accommodation",
            "name": "Hotel",
            "description": "A commercial establishment providing lodging, meals, and other guest services.",
            "iri": "http://www.owl-ontologies.com/travel.owl#Hotel"
        },
        {
            "type": "Accommodation",
            "name": "Hostel",
            "description": "An establishment that provides inexpensive food and lodging for a specific group of people, such as students, workers, or travelers.",
            "iri": "http://www.owl-ontologies.com/travel.owl#Hostel"
        }
    ]
    return documents