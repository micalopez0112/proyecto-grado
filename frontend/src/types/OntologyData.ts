export interface OntologyDataType {
  ontologyId: string;
  ontoData: Array<{
    name: string;
    data: Array<{
      classes: Array<{ name: string; iri: string }>;
      object_properties: Array<{ name: string; iri: string }>;
      data_properties: Array<{ name: string; iri: string }>;
    }>;
  }>;
}
