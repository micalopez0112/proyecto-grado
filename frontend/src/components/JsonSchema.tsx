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
    setLastClickedElement(element); // Update last clicked element
    console.log(element);
    // navigate("/testroute");
  };

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
            <div className="object-wrapper">
              <div
                className={`json-elem ${
                  lastClickedElement === parent + key ? "active" : ""
                }`}
                onClick={(e) => handleClickElement(e, parent + key)}
              >
                <strong>{key}:</strong>
              </div>

              <div
                className={`json-object-elem ${
                  lastClickedElement === parent + `${key}-object`
                    ? "active"
                    : ""
                }`}
                onClick={(e) => handleClickElement(e, parent + `${key}-object`)}
              >
                object
              </div>
            </div>
            <div className="object-properties">
              {renderProperties(value.properties, parent + key)}
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
              onClick={(e) => handleClickElement(e, parent + key)}
            >
              <strong>{key}:</strong> array
            </div>
            <div className="object-properties">
              {renderArrayItems(value.items, parent + key)}
            </div>
          </div>
        );
      }
      return (
        <div className="property-box" key={key}>
          <div
            className={`json-elem ${
              lastClickedElement === parent + key ? "active" : ""
            }`}
            onClick={(e) => handleClickElement(e, parent + key)}
          >
            <strong>{key}:</strong> {value.type}
          </div>
        </div>
      );
    });
  };

  const renderArrayItems = (items: JsonSchemaProperty, parent: string) => {
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
        <h1>JSON to JSON Schema Converter</h1>
        <textarea
          rows={30}
          cols={50}
          value={jsonInput}
          onChange={handleInputChange}
          placeholder="Enter JSON here"
        />
        <br />
        <button onClick={handleGenerateSchema}>Generate Schema</button>
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
