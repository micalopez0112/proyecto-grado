import React, { createContext, useContext, useState } from 'react';
import { OntologyDataType } from '../types/OntologyData';

export interface OntoElement{
  name?: string;
  iri?: string;
  range?:Array<OntoElement>;
}
interface OntoSelect{
  type?:"class"| "object_property" | "data_property";
  ontoElement: OntoElement;
}

interface Mapping{
  [jsonKey:string]: OntoElement[];
}
interface JsonSchemaContextProps {
  currentOntologyId?:string;
  setcurrentOntologyId: (value: string | undefined) => void;
  jsonSchemaContext: any;
  ontologyDataContext: any;
  setontologyDataContext: (value: any) => void;
  setJsonSchemaContext: (value: any) => void;
  JsonElementSelected: any;
  setJsonElementSelected: (value: any) => void;
  OntoElementSelected: OntoSelect;
  setOntoElementSelected: (value: any) => void;
  mappings: Mapping;
  setMappings: (mappings: Mapping) => void;
  addNewMapping : () => void;
  clearMappings: () => void;
}

/*
Arreglar tipos para que se use el JsonSchema interface declarado en JsonSchema.tsx

*/

 const Context = createContext<JsonSchemaContextProps>({
  currentOntologyId: undefined,
  setcurrentOntologyId: () => {},
  jsonSchemaContext: {},
  JsonElementSelected: {},
  setontologyDataContext: () => {},
  ontologyDataContext: {},
  OntoElementSelected: {type:undefined, ontoElement:{}},
  mappings: {},
  setJsonSchemaContext: () => {},
  setJsonElementSelected: () => {},
  setOntoElementSelected: () => {},
  setMappings:  () => {},
  addNewMapping: () =>{},
  clearMappings: () => {},
});

const ContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [JsonElementSelected, setJsonElementSelected] = useState<string>('');
  const [OntoElementSelected, setOntoElementSelected] = useState<OntoSelect>({
    type: undefined,
    ontoElement: {}
  });
  const [jsonSchemaContext, setJsonSchemaContext] = useState<Object>({});
  const [mappings, setMappings] = useState<Mapping>({});
  const [ontologyDataContext, setontologyDataContext] = useState<Object>({ontoData:[],ontologyId:''});
  const [currentOntologyId, setcurrentOntologyId] = useState<string | undefined>(undefined);


  const addNewMapping = () =>{
    console.log("Adding new mapping, actual mappings are: ", mappings);
    if(JsonElementSelected !== '' && OntoElementSelected.type !== undefined){
    if(OntoElementSelected.type === "class"){
      setMappings({
        ...mappings,
        [JsonElementSelected+'_value']: [...(mappings[JsonElementSelected] || []), OntoElementSelected.ontoElement]
      });
    }
    else if (OntoElementSelected.type === "object_property") {
      console.log("Object Property seleccionado en context", OntoElementSelected.ontoElement);
      console.log("JsonElementSelected en context", JsonElementSelected);
      console.log("Rango de OntoElementSelected que se está agregando en context", OntoElementSelected.ontoElement.range);
    
      const rango = OntoElementSelected.ontoElement.range;
      const key = { name: OntoElementSelected.ontoElement.name, iri: OntoElementSelected.ontoElement.iri };
      console.log("Key que se está agregando en context", key);
    
      // Combina todas las actualizaciones en un solo objeto
      setMappings((prevMappings) => {
        const newMappings = {
          ...prevMappings,
          [JsonElementSelected + '_key']: [
            ...(prevMappings[JsonElementSelected + '_key'] || []),
            key
          ]
        };
    
        if (rango) {
          newMappings[JsonElementSelected + '_value'] = [
            ...(prevMappings[JsonElementSelected + '_value'] || []),
            ...rango
          ];
        } else {
          console.error("Error al agregar mapeo de object property, no presenta rango");
        }
    
        return newMappings;
      });
    }
    else{
      console.log("JsonElementSelected en context",JsonElementSelected);
      setMappings({
        ...mappings,
        [JsonElementSelected]: [...(mappings[JsonElementSelected] || []), OntoElementSelected.ontoElement]
      });
    }
    setOntoElementSelected({type:undefined, ontoElement:{}});
    setJsonElementSelected('');
    }
    else{
      console.log("mappings vaciós");
      alert("Para agregar un mapeo primero debe seleccionarse un elemento del JSONSchema y de la ontología");
    }
  }

  const clearMappings = () => {
    setMappings({});
    setOntoElementSelected({type:undefined, ontoElement:{}});
    setJsonElementSelected('');
    setontologyDataContext({ontoData:[],ontologyId:''});
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
        clearMappings
      }}
    >
      {children}
    </Context.Provider>
  );
};

const useDataContext = () => useContext(Context);
export { ContextProvider, useDataContext };
