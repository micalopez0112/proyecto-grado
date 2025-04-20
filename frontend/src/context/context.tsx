import React, { createContext, useContext, useState, useEffect } from "react";
import { OntologyDataType, JsonSchema } from "../types";
import { toast } from "react-toastify";

export interface OntoElement {
  name?: string;
  iri?: string;
  range?: Array<OntoElement>;
}
interface OntoSelect {
  type?: "class" | "object_property" | "data_property";
  ontoElement: OntoElement;
}

interface Mapping {
  [jsonKey: string]: OntoElement[];
}
interface ContextProps {
  // External flow
  externalFlow: boolean;
  setExternalFlow: (value: boolean) => void;
  externalDatasetId: string;
  setExternalDatasetId: (value: string) => void;
  currentOntologyId?: string;
  setcurrentOntologyId: (value: string | undefined) => void;
  jsonSchemaContext: any;
  collectionPath: string;
  setCollectionPath: (value: string) => void;
  ontologyDataContext: any;
  setontologyDataContext: (value: any) => void;
  setJsonSchemaContext: (value: any) => void;
  JsonElementSelected: any;
  setJsonElementSelected: (value: any) => void;
  OntoElementSelected: OntoSelect;
  setOntoElementSelected: (value: any) => void;
  mappings: Mapping;
  setMappings: (mappings: Mapping) => void;
  addNewMapping: () => void;
  removeMapping: (
    key: string,
    elementToRemove: { name: string; iri: string }
  ) => void;
  clearMappings: () => void;
  resetMappingState: () => void;
  mappingProcessId: string;
  setMappingProcessId: (value: string) => void;
  outOfExternalFlow: () => void;
}

const Context = createContext<ContextProps>({
  externalFlow: false,
  externalDatasetId: "",
  currentOntologyId: undefined,
  jsonSchemaContext: {},
  JsonElementSelected: {},
  ontologyDataContext: {},
  OntoElementSelected: { type: undefined, ontoElement: {} },
  collectionPath: "",
  mappings: {},
  mappingProcessId: "",
  setcurrentOntologyId: () => {},
  setontologyDataContext: () => {},
  setJsonSchemaContext: () => {},
  setJsonElementSelected: () => {},
  setOntoElementSelected: () => {},
  setMappings: () => {},
  addNewMapping: () => {},
  removeMapping: () => {},
  clearMappings: () => {},
  setCollectionPath: () => {},
  resetMappingState: () => {},
  setMappingProcessId: () => {},
  setExternalFlow: () => {},
  setExternalDatasetId: () => {},
  outOfExternalFlow: () => {},
});

const ContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [externalFlow, setExternalFlow] = useState<boolean>(() =>
    JSON.parse(localStorage.getItem("externalFlow") || "false")
  );
  const [externalDatasetId, setExternalDatasetId] = useState<string>(
    () => localStorage.getItem("externalDatasetId") || ""
  );
  const [collectionPath, setCollectionPath] = useState<string>(
    () => localStorage.getItem("collectionPath") || ""
  );
  const [mappingProcessId, setMappingProcessId] = useState<string>("");
  const [JsonElementSelected, setJsonElementSelected] = useState<string>("");
  const [OntoElementSelected, setOntoElementSelected] = useState<OntoSelect>({
    type: undefined,
    ontoElement: {},
  });
  const [jsonSchemaContext, setJsonSchemaContext] = useState<JsonSchema | null>(
    null
  );
  const [mappings, setMappings] = useState<Mapping>({});
  const [ontologyDataContext, setontologyDataContext] =
    useState<OntologyDataType>({ ontoData: [], ontologyId: "" });
  const [currentOntologyId, setcurrentOntologyId] = useState<
    string | undefined
  >(undefined);

  const addNewMapping = () => {
    if (JsonElementSelected !== "" && OntoElementSelected.type !== undefined) {
      if (OntoElementSelected.type === "class") {
        setMappings({
          ...mappings,
          [JsonElementSelected]: [
            ...(mappings[JsonElementSelected] || []),
            OntoElementSelected.ontoElement,
          ],
        });
      } else if (OntoElementSelected.type === "object_property") {
        const rango = OntoElementSelected.ontoElement.range;
        const key = {
          name: OntoElementSelected.ontoElement.name,
          iri: OntoElementSelected.ontoElement.iri,
        };
        setMappings((prevMappings) => {
          const newMappings = {
            ...prevMappings,
            [JsonElementSelected]: [
              ...(prevMappings[JsonElementSelected] || []),
              key,
            ],
          };

          if (rango && rango.length > 0) {
            let claveMap = JsonElementSelected.endsWith("?key#array")
              ? JsonElementSelected.slice(0, JsonElementSelected.length - 10) //quitar ?key#array
              : JsonElementSelected.slice(0, JsonElementSelected.length - 4); //quitar ?key
            newMappings[claveMap + "?value"] = [
              ...(prevMappings[claveMap + "?value"] || []),
              ...rango,
            ];
          }
          return newMappings;
        });
      } else {
        // Data property
        setMappings({
          ...mappings,
          [JsonElementSelected]: [
            ...(mappings[JsonElementSelected] || []),
            OntoElementSelected.ontoElement,
          ],
        });
      }
      setOntoElementSelected({ type: undefined, ontoElement: {} });
      setJsonElementSelected("");
    } else {
      toast.error(
        "To add a mapping select one element from the JSON Schema and the Ontology"
      );
    }
  };

  const removeMapping = (
    key: string,
    elementToRemove: { name: string; iri: string }
  ) => {
    setMappings((prevMappings) => {
      const updatedMappings = { ...prevMappings };
      if (updatedMappings[key]) {
        updatedMappings[key] = updatedMappings[key].filter(
          (element) =>
            element.name !== elementToRemove.name ||
            element.iri !== elementToRemove.iri
        );

        const updatedKey = getUpdatedKey(key);
        if (updatedKey) {
          const objectPropertyRange = getRangeByObjectPropertyName(
            ontologyDataContext,
            elementToRemove.name
          );

          if (objectPropertyRange && objectPropertyRange.length > 0) {
            if (updatedMappings[updatedKey] !== undefined) {
              updatedMappings[updatedKey] = updatedMappings[updatedKey].filter(
                (element) =>
                  element.name !== objectPropertyRange[0].name ||
                  element.iri !== objectPropertyRange[0].iri
              );
              if (updatedMappings[updatedKey].length === 0) {
                // delete Object Property key if it has no elements
                delete updatedMappings[updatedKey];
              }
            }
          }
        }

        if (updatedMappings[key].length === 0) {
          delete updatedMappings[key];
        }
      }
      return updatedMappings;
    });
  };

  const getUpdatedKey = (key: string): string | null => {
    if (key.endsWith("?key")) {
      return key.slice(0, key.length - 4) + "?value";
    } else if (key.endsWith("?key#array")) {
      return key.slice(0, key.length - 10) + "?value";
    }
    return null;
  };

  const getRangeByObjectPropertyName = (
    ontologyData: OntologyDataType,
    objectPropertyName: string
  ): Array<{ name: string; iri: string }> => {
    for (const onto of ontologyData.ontoData) {
      for (const dataItem of onto.data) {
        for (const objectProperty of dataItem.object_properties) {
          if (objectProperty.name === objectPropertyName) {
            return Array.isArray(objectProperty.range)
              ? objectProperty.range
              : [objectProperty.range];
          }
        }
      }
    }
    return [];
  };

  const clearMappings = () => {
    setMappings({});
    setOntoElementSelected({ type: undefined, ontoElement: {} });
    setJsonElementSelected("");
  };

  const resetMappingState = () => {
    clearMappings();
    setJsonSchemaContext(null);
    setCollectionPath("");
    setMappingProcessId("");
  };

  const outOfExternalFlow = () => {
    setCollectionPath("");
    setExternalDatasetId("");
    setExternalFlow(false);
  };

  useEffect(() => {
    localStorage.setItem("externalFlow", JSON.stringify(externalFlow));
  }, [externalFlow]);

  useEffect(() => {
    if (externalFlow && collectionPath !== "") {
      //Va a cambiar pero no lo va a almacenar en el local storage
      localStorage.setItem("collectionPath", collectionPath);
    }
  }, [collectionPath]);

  useEffect(() => {
    localStorage.setItem("externalDatasetId", externalDatasetId);
  }, [externalDatasetId]);

  return (
    <Context.Provider
      value={{
        externalFlow,
        setExternalFlow,
        externalDatasetId,
        setExternalDatasetId,
        outOfExternalFlow,
        currentOntologyId,
        setcurrentOntologyId,
        jsonSchemaContext,
        setJsonSchemaContext,
        JsonElementSelected,
        setJsonElementSelected,
        setontologyDataContext,
        ontologyDataContext,
        OntoElementSelected,
        setOntoElementSelected,
        mappings,
        setMappings,
        addNewMapping,
        removeMapping,
        clearMappings,
        collectionPath,
        setCollectionPath,
        resetMappingState,
        mappingProcessId,
        setMappingProcessId,
      }}
    >
      {children}
    </Context.Provider>
  );
};

const useDataContext = () => useContext(Context);
export { ContextProvider, useDataContext };
