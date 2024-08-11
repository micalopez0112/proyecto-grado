import React, { useEffect, useState } from "react";
import "./JsonSchema.css";
import { json as generateJsonSchema } from "generate-schema";
import { useDataContext } from "../context/context.tsx";
import { useNavigate } from "react-router-dom";

// Define types for JSON Schema properties
interface JsonSchemaProperty {
  type: string;
  properties?: Record<string, JsonSchemaProperty>;
  items?: JsonSchemaProperty;
}

// Define types for JSON Schema
interface JsonSchema {
  type: string;
  properties: Record<string, JsonSchemaProperty>;
}

const Json: React.FC = () => {
  const [jsonInput, setJsonInput] = useState<string>("");
  const [jsonSchema, setJsonSchema] = useState<JsonSchema | null>(null);
  const [lastClickedElement, setLastClickedElement] = useState<string | null>(
    null
  ); // New state
  const { setJsonSchemaContext, setJsonElementSelected, JsonElementSelected } =
    useDataContext();
  const navigate = useNavigate();

  // useEffect(() => {
  //   console.log("jsonSchemaContext:", jsonSchemaContext);
  //   console.log("JsonElementSelected:", JsonElementSelected);
  // }, [jsonSchemaContext, JsonElementSelected]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setJsonInput(e.target.value);
  };

  const handleClickElement = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string
  ) => {
    setJsonElementSelected(element);
    setLastClickedElement(element); // Fix this
    console.log(element);
    // navigate("/testroute");
  };

  const handleClickSimpleProperty = (e: React.MouseEvent<HTMLDivElement>,
    element: string,
    type:string) => {
      setJsonElementSelected(element+'_key#'+type);
      setLastClickedElement(element); // Fix this
      console.log(element+'_key#'+type);
    }

  const handleGenerateSchema = () => {
    try {
      const jsonData = JSON.parse(jsonInput);
      const schema = generateJsonSchema(jsonData);
      setJsonSchema(schema);
      setJsonSchemaContext(schema);
    } catch (error) {
      console.error("Invalid JSON input");
      setJsonSchema(null);
    }
  };

  const renderProperties = (
    properties: Record<string, JsonSchemaProperty>,
    parent: string
  ) => {
    return Object.entries(properties).map(([key, value]) => {
      if (value.type === "object" && value.properties) {
        return (
          <div className="property-box" key={key}>
              <div
                className={`json-elem ${
                  lastClickedElement === parent + key ? "active" : ""
                }`}
                onClick={(e) => 
                  handleClickElement(e, parent ? parent +'-'+key : key)
                }
              >
                <strong>{key}:</strong> object
              </div>
            <div className="object-properties">
              {renderProperties(value.properties, parent ? parent +'-'+key : key)}
            </div>
          </div>
        );
      }
      if (value.type === "array" && value.items) {
        return (
          <div className="property-box" key={key}>
            <div
              className={`json-elem ${
                lastClickedElement === parent + key ? "active" : ""
              }`}
              onClick={(e) => handleClickElement(e, parent +'-'+ key)}
            >
              <strong>{key}:</strong> array
            </div>
            <div className="object-properties">
              {renderArrayItems(value.items, parent+'-'+ key)}
            </div>
          </div>
        );
      }
      return (
        //simple property
        <div className="property-box" key={key}>
          <div
            className={`json-elem ${
              lastClickedElement === parent + key ? "active" : ""
            }`}
            onClick={(e) => handleClickSimpleProperty(e, parent +'-'+ key,value.type)}
          >
            <strong>{key}:</strong> {value.type}
          </div>
        </div>
      );
    });
  };

  const renderArrayItems = (items: JsonSchemaProperty, parent: string) => {
    //checkear invocaciones de handleClickElement y el valor de parent
    if (items.type === "object" && items.properties) {
      return (
        <>
          <div
            className={`json-elem ${
              lastClickedElement === parent + `items` ? "active" : ""
            }`}
            onClick={(e) => handleClickElement(e, parent + `items`)}
          >
            <strong>items:</strong> object
          </div>
          <div className="object-properties">
            {renderProperties(items.properties, parent + `items`)}
          </div>
        </>
      );
    }
    return (
      <>
        <div
          className={`json-elem ${
            lastClickedElement === parent + `items` ? "active" : ""
          }`}
          onClick={(e) => handleClickElement(e, parent + `items`)}
        >
          <strong>items:</strong> {items.type}
        </div>
      </>
    );
  };

  return (
    <div className="container">
      <div className="json-input">
      <span style={{fontFamily:'Roboto',fontSize:'25px', marginBottom:'10px'}}>JSON to JSON Schema Converter</span>
        <textarea
          rows={20}
          cols={35}
          value={jsonInput}
          onChange={handleInputChange}
          placeholder="Enter JSON here"
        />
        <br />
        <div style={{
          display: "flex",
          justifyContent: "center",
          marginTop: "10px",
        }}>
        <button onClick={handleGenerateSchema}>Generate Schema</button>
        </div>
         </div>
      {jsonSchema && (
        <div className="json-schema-container">
          {/* <div className="json-schema">
            <h2>Generated JSON Schema</h2>
            <pre className="json-schema">
              {JSON.stringify(jsonSchema, null, 2)}
            </pre>
      </div>*/ }
          <div className="json-schema">
            {JsonElementSelected !== "" ? <p>{JsonElementSelected}</p> : null}
            {renderProperties(jsonSchema.properties, "")}
          </div>
        </div>
      )}
    </div>
  );
};

export default Json;
