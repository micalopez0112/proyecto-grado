export interface OntologyDataType {
  ontologyId: string;
  ontoData: Array<{
    name: string;
    data: Array<{
      classes: Array<{ name: string; iri: string }>;
      object_properties: Array<{
        name: string;
        iri: string;
        range: Array<{ name: string; iri: string }>;
      }>;
      data_properties: Array<{ name: string; iri: string }>;
    }>;
  }>;
}

export const getRangeByObjectPropertyName = (
  ontologyData: OntologyDataType,
  objectPropertyName: string
): Array<{ name: string; iri: string }> | undefined => {
  for (const onto of ontologyData.ontoData) {
    for (const dataItem of onto.data) {
      for (const objectProperty of dataItem.object_properties) {
        if (objectProperty.name === objectPropertyName) {
          return objectProperty.range;
        }
      }
    }
  }
  return undefined;
};
