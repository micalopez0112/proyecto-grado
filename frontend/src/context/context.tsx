import React, { createContext, useContext, useState } from 'react';
import { OntologyDataType,getRangeByObjectPropertyName, JsonSchema} from '../types/index.ts';


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
  removeMapping: (key: string, elementToRemove: { name: string; iri: string }) => void;
  clearMappings: () => void;
}

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
  removeMapping: () => {},
  clearMappings: () => {},
});

const ContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [JsonElementSelected, setJsonElementSelected] = useState<string>('');
  const [OntoElementSelected, setOntoElementSelected] = useState<OntoSelect>({
    type: undefined,
    ontoElement: {}
  });
  const [jsonSchemaContext, setJsonSchemaContext] = useState<JsonSchema | null>(null);
  const [mappings, setMappings] = useState<Mapping>({});
  const [ontologyDataContext, setontologyDataContext] = useState<OntologyDataType>({ontoData:[],ontologyId:''});
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
    
      // Mejor hacer todas las las actualizaciones de una sino hay problemas con el estado
      setMappings((prevMappings) => {
        const newMappings = {
          ...prevMappings,
          [JsonElementSelected.endsWith('_key#array')? JsonElementSelected : JsonElementSelected+'_key']: [
            ...(prevMappings[JsonElementSelected.endsWith('_key#array')? JsonElementSelected : JsonElementSelected+'_key'] || []),
            key
          ]
        };
    
        if (rango) {
          let claveMap = JsonElementSelected.endsWith('_key#array')?JsonElementSelected.slice(0,JsonElementSelected.length-10):JsonElementSelected;
          newMappings[claveMap + '_value'] = [
            ...(prevMappings[claveMap + '_value'] || []),
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

  const removeMapping = (key: string, elementToRemove:{ name: string; iri: string }) => {
    setMappings((prevMappings) => {
      const updatedMappings = { ...prevMappings };
      if (updatedMappings[key]) {

        //TODO:check if it is an object property mapping with _key
        //if so, remove the _key and _value mappings{

        updatedMappings[key] = updatedMappings[key].filter(
            (element) => element.name !== elementToRemove.name || element.iri !== elementToRemove.iri
        );
        if(key.endsWith('_key') || key.endsWith('_key#array')){
          //obtener el rango de la object property
          const objectPropertyRange = getRangeByObjectPropertyName(ontologyDataContext,elementToRemove.name);
          console.log("El rango de la object property que se está eliminando es: ", objectPropertyRange);
          /*updatedMappings[key.slice(0,key.length-4)+'_value'].filter(
            (element) => element.name !== elementToRemove.name || element.iri !== elementToRemove.iri
          ); *///fix
          //falta caso de array
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

  const clearMappings = () => {
    setMappings({});
    setOntoElementSelected({type:undefined, ontoElement:{}});
    setJsonElementSelected('');
    setontologyDataContext({ontoData:[],ontologyId:''});
    setJsonSchemaContext(null);
    setcurrentOntologyId(undefined);
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
        clearMappings
      }}
    >
      {children}
    </Context.Provider>
  );
};

const useDataContext = () => useContext(Context);
export { ContextProvider, useDataContext };
