import React, { createContext, useContext, useState } from 'react';

interface OntoElement{
  name?: string;
  iri?: string;
}
interface Mapping{
  [jsonKey:string]: OntoElement[];
}
interface JsonSchemaContextProps {
  jsonSchemaContext: any;
  ontologyDataContext: Object;
  setJsonSchemaContext: (value: any) => void;
  JsonElementSelected: any;
  setJsonElementSelected: (value: any) => void;
  OntoElementSelected: OntoElement;
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
  jsonSchemaContext: {},
  JsonElementSelected: {},
  ontologyDataContext: {},
  OntoElementSelected: {},
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
  const [OntoElementSelected, setOntoElementSelected] = useState<Object>({});
  const [jsonSchemaContext, setJsonSchemaContext] = useState<Object>({});
  const [mappings, setMappings] = useState<Mapping>({});
  const [ontologyDataContext, setOntologyDataContext] = useState<Object>({});


  const addNewMapping = () =>{
    console.log("Adding new mapping");
    setMappings({
      ...mappings,
      [JsonElementSelected]: [...(mappings[JsonElementSelected] || []), OntoElementSelected]
    });
    setOntoElementSelected({});
    setJsonElementSelected('');
  }

  const clearMappings = () => {
    setMappings({});
    setOntoElementSelected({});
    setJsonElementSelected('');
  };

  return (
    <Context.Provider
      value={{
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
