import React from "react";
import { useDataContext } from "../context/context.tsx";

const Test = () => {
  const { JsonElementSelected } = useDataContext();

  console.log("en test:" + JsonElementSelected);

  return (
    <div>
      <h1>Test</h1>
      <p>
        Valor de Json Element Context: <strong>{JsonElementSelected}</strong>
      </p>
    </div>
  );
};

export default Test;
