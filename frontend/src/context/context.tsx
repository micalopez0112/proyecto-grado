import React, { createContext, useContext, useState } from 'react';

interface OntoElement{
  name?: string;
  iri?: string;
}
interface JsonSchemaContextProps {
  jsonSchemaContext: any;
  ontologyDataContext: Object;
  setJsonSchemaContext: (value: any) => void;
  JsonElementSelected: any;
  setJsonElementSelected: (value: any) => void;
  OntoElementSelected: OntoElement;
  setOntoElementSelected: (value: any) => void;
}

/*
Arreglar tipos para que se use el JsonSchema interface declarado en JsonSchema.tsx

*/

 const Context = createContext<JsonSchemaContextProps>({
  jsonSchemaContext: {},
  setJsonSchemaContext: () => {},
  JsonElementSelected: {},
  ontologyDataContext: {},
  OntoElementSelected: {},
  setJsonElementSelected: () => {},
  setOntoElementSelected: () => {},
});

const ContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [JsonElementSelected, setJsonElementSelected] = useState<string>('');
  const [OntoElementSelected, setOntoElementSelected] = useState<Object>({});
  const [jsonSchemaContext, setJsonSchemaContext] = useState<Object>({});
  const [mappings, setMappings] = useState<Object []>([]);
  const [ontologyDataContext, setOntologyDataContext] = useState<Object>({});

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
      }}
    >
      {children}
    </Context.Provider>
  );
};

const useDataContext = () => useContext(Context);
export { ContextProvider, useDataContext };
