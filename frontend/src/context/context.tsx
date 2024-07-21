import React, { createContext, useContext, useState } from 'react';

interface JsonSchemaContextProps {
  jsonSchemaContext: any;
  setJsonSchemaContext: (value: any) => void;
  JsonElementSelected: any;
  setJsonElementSelected: (value: any) => void;
  OntoElementSelected: any;
  setOntoElementSelected: (value: any) => void;
}

/*
Arreglar tipos para que se use el JsonSchema interface declarado en JsonSchema.tsx

*/

 const Context = createContext<JsonSchemaContextProps>({
  jsonSchemaContext: {},
  setJsonSchemaContext: () => {},
  JsonElementSelected: {},
  OntoElementSelected: {},
  setJsonElementSelected: () => {},
  setOntoElementSelected: () => {},
});

const ContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [JsonElementSelected, setJsonElementSelected] = useState<string>('');
  const [OntoElementSelected, setOntoElementSelected] = useState<string>('');
  const [jsonSchemaContext, setJsonSchemaContext] = useState<Object>({});

  return (
    <Context.Provider
      value={{
        jsonSchemaContext,
        setJsonSchemaContext,
        JsonElementSelected,
        setJsonElementSelected,
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
