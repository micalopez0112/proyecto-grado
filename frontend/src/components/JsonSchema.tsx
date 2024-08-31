import React, { useEffect, useState } from "react";
import "./JsonSchema.css";
import { json as generateJsonSchema } from "generate-schema";
import { useDataContext } from "../context/context.tsx";
import { useNavigate } from "react-router-dom";
import { JsonSchema, JsonSchemaProperty } from "../types";

const Json: React.FC = () => {
  const [jsonInput, setJsonInput] = useState<string>("");
  const [jsonSchema, setJsonSchema] = useState<JsonSchema | null>(null);
  const [lastClickedElement, setLastClickedElement] = useState<string | null>(
    null
  );
  const {
    setJsonSchemaContext,
    jsonSchemaContext,
    setJsonElementSelected,
    JsonElementSelected,
  } = useDataContext();

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

  const handleClickSimpleProperty = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string,
    type: string
  ) => {
    setJsonElementSelected(element + "_key#" + type);
    setLastClickedElement(element); // Fix this
  };

  const handleClickArrayProperty = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string
  ) => {
    setJsonElementSelected(element + "_key#array");
    setLastClickedElement(element); // Fix this
  };

  // const handleGenerateSchema = () => {
  //   try {
  //     const jsonData = JSON.parse(jsonInput);
  //     const schema = generateJsonSchema(jsonData);
  //     console.log("##GENERATED SCHEMA##", schema);
  //     setJsonSchema(schema);
  //     setJsonSchemaContext(schema);
  //   } catch (error) {
  //     console.error("Invalid JSON input");
  //     setJsonSchema(null);
  //   }
  // };

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
                handleClickElement(e, parent ? parent + "-" + key : key)
              }
            >
              <strong>{key}:</strong> object
            </div>
            <div className="object-properties">
              {renderProperties(
                value.properties,
                parent ? parent + "-" + key : key
              )}
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
              onClick={(e) => handleClickArrayProperty(e, parent + "-" + key)}
            >
              <strong>{key}:</strong> array
            </div>
            <div className="object-properties">
              {renderArrayItems(value.items, parent + "-" + key)}
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
            onClick={(e) =>
              handleClickSimpleProperty(e, parent + "-" + key, value.type)
            }
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
          {/* <div
            className={`json-elem ${
              lastClickedElement === parent + `items` ? "active" : ""
            }`}
            onClick={(e) => handleClickElement(e, parent + `items`)}
          >
            <strong>items:</strong> object
          </div> */}
          <div className="object-properties">
            {renderProperties(items.properties, parent)}
          </div>
        </>
      );
    }
    return (
      <>
        <div
          className={`json-arrayItem-elem ${
            lastClickedElement === parent + `items` ? "active" : ""
          }`}
          onClick={(e) =>
            console.log("clicked array item, doesn´t do anything")
          }
        >
          <strong>array items:</strong> {items.type}
        </div>
      </>
    );
  };

  return (
    <div className="container">
      <div className="title-wrapper">
        <h1 className="title">JSON Schema</h1>
      </div>

      {/* <div className="json-input">
        <span
          style={{
            fontFamily: "Roboto",
            fontSize: "25px",
            marginBottom: "10px",
          }}
        >
          JSON to JSON Schema Converter
        </span>
        <textarea
          rows={20}
          cols={35}
          value={jsonInput}
          onChange={handleInputChange}
          placeholder="Enter JSON here"
        />
        <br />
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginTop: "10px",
          }}
        >
          <button className="button" onClick={handleGenerateSchema}>
            Generate Schema
          </button>
        </div>
      </div> */}
      {jsonSchemaContext && (
        <div className="json-schema-container">
          <div className="json-schema">
            {JsonElementSelected !== "" ? <p>{JsonElementSelected}</p> : null}
            {jsonSchemaContext
              ? renderProperties(jsonSchemaContext.properties, "")
              : null}
          </div>
        </div>
      )}
    </div>
  );
};

export default Json;