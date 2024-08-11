import React, { createContext, useContext, useState } from 'react';

interface OntoElement{
  name?: string;
  iri?: string;
}
interface OntoSelect{
  type?:"class"| "object_property" | "data_property";
  ontoElement: OntoElement;
}

interface Mapping{
  [jsonKey:string]: OntoElement[];
}
interface JsonSchemaContextProps {
  currentMappingProcessId?:number;
  setCurrentMappingProcessId: (value: number | undefined) => void;
  jsonSchemaContext: any;
  ontologyDataContext: Object;
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
  currentMappingProcessId: undefined,
  setCurrentMappingProcessId: () => {},
  jsonSchemaContext: {},
  JsonElementSelected: {},
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
  const [ontologyDataContext, setOntologyDataContext] = useState<Object>({});
  const [currentMappingProcessId, setCurrentMappingProcessId] = useState<number | undefined>(undefined);


  const addNewMapping = () =>{
    console.log("Adding new mapping");
    if(OntoElementSelected.type === "class"){
      setMappings({
        ...mappings,
        [JsonElementSelected+'_value']: [...(mappings[JsonElementSelected] || []), OntoElementSelected.ontoElement]
      });
    }
    else if (OntoElementSelected.type === "object_property"){
      setMappings({
        ...mappings,
        [JsonElementSelected+'_key']: [...(mappings[JsonElementSelected] || []), OntoElementSelected.ontoElement]
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
    //diferenciar según casos?
  }

  const clearMappings = () => {
    setMappings({});
    setOntoElementSelected({type:undefined, ontoElement:{}});
    setJsonElementSelected('');
  };

  return (
    <Context.Provider
      value={{
        currentMappingProcessId,
        setCurrentMappingProcessId,
        jsonSchemaContext,
        setJsonSchemaContext,
        JsonElementSelected,
        setJsonElementSelected,
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
