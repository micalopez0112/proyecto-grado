from owlready2 import *
from bson import ObjectId
from app.domain.mapping.models import MappingProcess, get_mapping_process, MappingRequest, MappingResponse, OntologyDocument
from app.domain.mapping.service import process_mapping

from app.database import onto_collection, mapping_process_collection, jsonschemas_collection
import random


def data_prop_range_to_str(name): ##used to take the data property range as a string
  class_name = re.search("'(.+?)'", name)
  if class_name:
    return class_name.group(1)
  return None


##def get_ontology_info_from_uri(/*uri, is_file, incomplete = True):
async def get_ontology_info_from_pid(ontology_id):
    # mappingProcess = get_mapping_process(process_id)
    # onto = mappingProcess.ontology
    onto_id = ObjectId(ontology_id)
    ontology_docu = await onto_collection.find_one({'_id': onto_id})
    if ontology_docu is None:
        ##handle error
        return None
    
    ontology_docu['id'] = str(ontology_docu['_id'])
    ontology_document = OntologyDocument(**ontology_docu)
    print("El ontologyDocument es: ", ontology_document)
    if ontology_document.type == "FILE":
        ontology_path = ontology_document.file
        ontology = get_ontology(ontology_path).load()
    else: ##document.type == "URI"
        ontology = get_ontology(str(ontology_document.uri)).load()

    onto_classes = list(ontology.classes())
    onto_object_properties = list(ontology.object_properties())
    onto_data_properties = list(ontology.data_properties())
    
    ## Transform ontology elements to string names to be serializable
    classes = [
      {
        'name':i.label[0] if len(i.label) > 0 else i.name, 
        'iri': i.iri,
        'equivalent_to': [elem.iri for elem in i.equivalent_to if elem is not None and getattr(elem, 'iri', None)],
        'is_a': [elem.iri for elem in i.is_a if (elem is not None and getattr(elem, 'name', None) and elem.name != 'Thing')],
      } for i in onto_classes if getattr(i, 'iri', None)
    ]
    obj_properties = [
      {
          'name':i.label[0] if len(i.label) > 0 else i.name,
          'iri': i.iri,
          'domain': [elem.iri for elem in i.domain if elem is not None and getattr(elem, 'iri', None)],
          'range': [elem.iri for elem in i.range if elem is not None and getattr(elem, 'iri', None)],
      } for i in onto_object_properties if getattr(i, 'iri', None)]
    data_properties = [
      {
        'name':i.label[0] if len(i.label) > 0 else i.name,
        'domain': [elem.iri for elem in i.domain if elem is not None and getattr(elem, 'iri', None)],
        'range': [{data_prop_range_to_str(str(elem))} for elem in i.range if elem is not None],
        'iri': i.iri
      } for i in onto_data_properties if getattr(i, 'iri', None)]

    res = [
        { "classes": classes}, 
        { "object_properties": obj_properties}, 
        { "data_properties": data_properties}
    ]
    close_world(ontology)## The ontology must be closed to avoid inconsistencies
    return res

def graph_generator(ontology_elements, map_proccess):
    graph = {}
    nodes = []
    edges = []
    try:
        onto_mapping_elems = [
           onto_elem['iri'] for _, map_elem in map_proccess.items() for onto_elem in map_elem 
        ]
        # print(onto_mapping_elems)
        current_edges_per_node = {}
        for class_node in ontology_elements[0]['classes']:
            node = { "id": class_node['iri'], "label": class_node['name']}
            # Check if the class is subClass of another class 
            if (len(class_node['is_a']) > 0):
                for parent_class in class_node['is_a']:
                    from_iri = class_node['iri']
                    to_iri = parent_class
                    new_edge = { 
                        "id": f'{from_iri}-rdfs:subClassOf-{to_iri}', 
                        "from": from_iri, 
                        "to": to_iri,
                        "label": 'rdfs:subClassOf',
                        "dashes": True,
                        "arrows": 'from',
                    }
                    node_pair_key = from_iri+to_iri if from_iri <= to_iri else to_iri+from_iri
                    if not node_pair_key in current_edges_per_node:
                        current_edges_per_node[node_pair_key]= 1
                    else:
                        current_edges_per_node[node_pair_key] += 1
                    edges.append(new_edge)
            if class_node['iri'] in onto_mapping_elems:
                node['color'] = "#5dbb63"
                # Check if the class has equivalent elements
                if (len(class_node['equivalent_to']) > 0):
                    from_iri = class_node['iri']
                    to_iri = class_node['equivalent_to'][0].iri
                    node_pair_key = from_iri+to_iri if from_iri <= to_iri else to_iri+from_iri

                    if not node_pair_key in current_edges_per_node:
                        current_edges_per_node[node_pair_key]= 1
                    else:
                        current_edges_per_node[node_pair_key] += 1
                    roundness_coeficient = current_edges_per_node[node_pair_key] * 0.2
                    new_edge = { 
                        "id": f'{from_iri}-owl:sameAs-{to_iri}', 
                        "from": from_iri, 
                        "to": to_iri, 
                        "label": '',
                        'color': '#CC5500',
                        "smooth": {"type": 'curvedCW', "enabled": True if current_edges_per_node[node_pair_key] > 1 else False, "type": 'curvedCW', "roundness": roundness_coeficient if current_edges_per_node[node_pair_key] > 1 else 0}
                    }
                    edges.append(new_edge)
            nodes.append(node)
        for edge in ontology_elements[1]['object_properties']:
            if len(edge['range']) > 0 and len(edge['domain']) > 0:
                node_pair_key = edge['range'][0]+edge['domain'][0] if edge['range'][0] <= edge['domain'][0] else edge['domain'][0]+edge['range'][0]
                if not node_pair_key in current_edges_per_node:
                    current_edges_per_node[node_pair_key] = 1
                else:
                    current_edges_per_node[node_pair_key] += 1
            roundness_coeficient = current_edges_per_node[node_pair_key] * 0.2

            new_edge = { 
                "id": edge['iri'], 
                "from": edge['domain'][0] if len(edge['domain']) > 0 else None, 
                "to": edge['range'][0] if len(edge['range']) > 0 else None, 
                "label": edge['name'],
                "smooth": {"type": 'curvedCW', "enabled": True if current_edges_per_node[node_pair_key] > 1 else False, "type": 'curvedCW', "roundness": roundness_coeficient if current_edges_per_node[node_pair_key] > 1 else 0}

            }
            if edge['iri'] in onto_mapping_elems:
                new_edge['color'] = "#5dbb63"
                new_edge['width'] = 2
            edges.append(new_edge)
        for edge in ontology_elements[2]['data_properties']:
            if (len(edge['range']) > 0):
                id_node = random.random()
                node = { "id": id_node, "label": edge['range'][0], 'color': '#FFFF00', 'font': {'color': 'black'}}
                nodes.append(node)
                new_edge = { 
                    "id": edge['iri'], 
                    "from": edge['domain'][0] if len(edge['domain']) > 0 else None, 
                    "to": id_node if len(edge['range']) > 0 else None, 
                    "label": edge['name'],
                }
                if edge['iri'] in onto_mapping_elems:
                    new_edge['color'] = "#5dbb63"
                    new_edge['width'] = 2
                edges.append(new_edge)
        graph['edges'] = edges
        graph['nodes'] = nodes
        print("Graph to show generated successfully", graph)
    except Exception as e:
        print("Exception during map graph generation ", e)
    return graph