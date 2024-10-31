import React, { createContext, useContext, useState } from "react";
import { OntologyDataType, JsonSchema } from "../types";

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
interface JsonSchemaContextProps {
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
}

const Context = createContext<JsonSchemaContextProps>({
  currentOntologyId: undefined,
  jsonSchemaContext: {},
  JsonElementSelected: {},
  ontologyDataContext: {},
  OntoElementSelected: { type: undefined, ontoElement: {} },
  collectionPath: "",
  mappings: {},
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
});

const ContextProvider = ({ children }: { children: React.ReactNode }) => {
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
  const [collectionPath, setCollectionPath] = useState<string>("");

  const addNewMapping = () => {

    console.log("Adding new mapping, actual mappings are: ", mappings);
    if (JsonElementSelected !== "" && OntoElementSelected.type !== undefined) {
      console.log("ONTO ELEMENT SELECTED", OntoElementSelected);
      if (OntoElementSelected.type === "class") {
        setMappings({
          ...mappings,
          [JsonElementSelected]: [
            ...(mappings[JsonElementSelected] || []),
            OntoElementSelected.ontoElement,
          ],
        });
      } else if (OntoElementSelected.type === "object_property") {
        console.log(
          "Object Property seleccionado en context",
          OntoElementSelected.ontoElement
        );
        console.log("JsonElementSelected en context", JsonElementSelected);
        console.log(
          "Rango de OntoElementSelected que se está agregando en context",
          OntoElementSelected.ontoElement.range
        );

        const rango = OntoElementSelected.ontoElement.range;
        console.log("RANGO", rango);
        const key = {
          name: OntoElementSelected.ontoElement.name,
          iri: OntoElementSelected.ontoElement.iri,
        };
        console.log("Key que se está agregando en context", key);

        // Mejor hacer todas las las actualizaciones de una sino hay problemas con el estado
        // setMappings((prevMappings) => {
        //   const newMappings = {
        //     ...prevMappings,
        //     [JsonElementSelected.endsWith("_key#array")
        //       ? JsonElementSelected
        //       : JsonElementSelected + "_key"]: [
        //       ...(prevMappings[
        //         JsonElementSelected.endsWith("_key#array")
        //           ? JsonElementSelected
        //           : JsonElementSelected + "_key"
        //       ] || []),
        //       key,
        //     ],
        //   };
          setMappings((prevMappings) => {
            const newMappings = {
              ...prevMappings,
              [JsonElementSelected]: [
                ...(prevMappings[JsonElementSelected] || []),
                key,
              ],
            };

          //acá tendría que preguntar si el object ya está mappeado no hago nada
          //y si no está mappeado agrego el _value con el rango

          //Enrealidad se haría en el ontologyData.tsx al buscar en mappings
          //si el _key es seleccionado y el _value aún no => se abre el modal
          if (rango && rango.length >0 ) {
            console.log("RANGO RANGO RANGO", rango);
            let claveMap = JsonElementSelected.endsWith("_key#array")
              ? JsonElementSelected.slice(0, JsonElementSelected.length - 10)//quitar _key#array
              : JsonElementSelected.slice(0, JsonElementSelected.length - 4);//quitar _key
            console.log("ClaveMap", claveMap);
            newMappings[claveMap + "_value"] = [
              ...(prevMappings[claveMap + "_value"] || []),
              ...rango,
            ];
          } else {
            console.log(
              "Se mapeó Object Property pero no se agregó el rango siendo el mismo: ", rango
            );
          }
          return newMappings;
        });
      } else {
        // Data property
        console.log("JsonElementSelected en context", JsonElementSelected);
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
      console.log("mappings vaciós");
      alert(
        "Para agregar un mapeo primero debe seleccionarse un elemento del JSONSchema y de la ontología"
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
        //TODO:check if it is an object property mapping with _key
        //if so, remove the _key and _value mappings{

        updatedMappings[key] = updatedMappings[key].filter(
          (element) =>
            element.name !== elementToRemove.name ||
            element.iri !== elementToRemove.iri
        );
        if (key.endsWith("_key") || key.endsWith("_key#array")) {
          //obtener el rango de la object property
          const objectPropertyRange = getRangeByObjectPropertyName(
            ontologyDataContext,
            elementToRemove.name
          );
          if (objectPropertyRange && objectPropertyRange.length > 0) {
            const objectPropertyRangeNames = objectPropertyRange.map(
              (rangeItem) => rangeItem.name
            );
            console.log(
              "El rango de la object property que se está eliminando es: ",
              objectPropertyRange
            );
            console.log(
              "De este rango los nombres son: ",
              objectPropertyRangeNames
            );
            console.log(
              "El rango que se quiere eliminar es: ",
              objectPropertyRange[0].name
            );
            console.log(
              "Entradas de la key que se quiere eliminar: ",
              updatedMappings[key.slice(0, key.length - 4) + "_value"]
            );
            if (updatedMappings[key.slice(0, key.length - 4) + "_value"] != undefined){
              updatedMappings[key.slice(0, key.length - 4) + "_value"] =
              updatedMappings[key.slice(0, key.length - 4) + "_value"].filter(
                //fix needed to work with arrays and multiple values in range
                (element) =>
                  element.name !== objectPropertyRange[0].name ||
                  element.iri !== objectPropertyRange[0].iri
              );
            console.log(
              "Entradas de la key después de eliminar: ",
              updatedMappings[key.slice(0, key.length - 4) + "_value"]
            );
            }
          } else {
            //handle not range, POSSIBLE??
          }
          //falta caso de array sería con slice -10
        }
        // Delete key if it has no elements
        // necessary?
        if (updatedMappings[key].length === 0) {
          delete updatedMappings[key];
        }
      }
      return updatedMappings;
    });
  };

  const getRangeByObjectPropertyName = (
    ontologyData: OntologyDataType,
    objectPropertyName: string
  ): Array<{ name: string; iri: string }> => {
    console.log("Ontología del detail", ontologyData);
    for (const onto of ontologyData.ontoData) {
      for (const dataItem of onto.data) {
        for (const objectProperty of dataItem.object_properties) {
          if (objectProperty.name === objectPropertyName) {
            console.log("ENTRO BIEN BIEN");
            console.log(
              "El rango de la object property es: ",
              objectProperty.range
            );
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
    console.log("Se ejecuta clear mappings");
    setMappings({});
    setOntoElementSelected({ type: undefined, ontoElement: {} });
    setJsonElementSelected("");
  };

  return (
    <Context.Provider
      value={{
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
        setCollectionPath
      }}
    >
      {children}
    </Context.Provider>
  );
};

const useDataContext = () => useContext(Context);
export { ContextProvider, useDataContext };
