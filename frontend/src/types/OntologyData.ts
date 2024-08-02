export interface OntologyDataType {
  ontoData: Array<{
    name: string;
    data: Array<{
      classes: Array<{ name: string; iri: string }>;
      object_properties: Array<{ name: string; iri: string }>;
      data_properties: Array<{ name: string; iri: string }>;
    }>;
  }>;
}
