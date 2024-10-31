import React from "react";
import "./JsonSchema.css";
import { useDataContext } from "../context/context.tsx";
import { JsonSchemaProperty } from "../types";

const Json: React.FC = () => {
  const { jsonSchemaContext, setJsonElementSelected, JsonElementSelected } =
    useDataContext();

  const handleClickElement = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string
  ) => {
    console.log("Element parameter: ", element);
    setJsonElementSelected(element);
  };

  const handleClickSimpleProperty = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string,
    type: string
  ) => {
    setJsonElementSelected(element + "_key#" + type);
    console.log("element: " + element);
  };

  const handleClickArrayProperty = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string
  ) => {
    setJsonElementSelected(element + "_key#array");
    console.log("element: " + element);
  };

  const renderProperties = (
    properties: Record<string, JsonSchemaProperty>,
    parent: string
  ) => {
    if(parent === ""){
      return (
        <div>
          <div className="property-box" key={"rootObject"}>
            <div
              className={`json-elem ${
                JsonElementSelected === parent
                  ? "active"
                  : ""
              }`}
              onClick={(e) =>
                handleClickElement(e, "rootObject_value") //se tiene que mapear a class
              }
            >
              <strong>rootObject:</strong> 
            </div>
            <div className="object-properties">
              {renderProperties(
                properties,
                "rootObject"
              )}
            </div>
          </div>
        </div>
      )
    }
    else{
      return Object.entries(properties).map(([key, value]) => {
        if (value.type === "object" && value.properties) {
          return (
            <div className="property-box" key={key}>
              <div
                className={`json-elem ${
                  JsonElementSelected === (parent ? parent + "-" + key : key)
                    ? "active"
                    : ""
                }`}
                onClick={(e) =>
                  handleClickElement(e, parent ? parent + "-" + key+ "_key"  : key+ "_key")
                }
              >
                <strong>{key}:</strong> 
              </div>
              {
                <div key={key + '_value'} className={`json-elem ${
                  JsonElementSelected === (parent ? parent + "-" + key : key )
                    ? "active"
                    : ""
                }`}
                  style={{marginLeft:'20px'}}
                  onClick={(e) =>
                    handleClickElement(e, parent ? parent + "-" + key + "_value" : key + "_value")
                  }>
                    <strong>object</strong>
                </div>
              }
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
                  JsonElementSelected === (parent ? parent + "-" + key : key)
                    ? "active"
                    : ""
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
          <div className="property-box" key={key}>
            <div
              className={`json-elem ${
                JsonElementSelected === (parent ? parent + "-" + key : key)
                  ? "active"
                  : ""
              }`}
              onClick={(e) =>
                handleClickSimpleProperty(e, parent + "-" + key, value.type)
              }
            >
              <strong>{key}:</strong> {value.type}
            </div>
          </div>
        );
      });}
  };

  const renderArrayItems = (items: JsonSchemaProperty, parent: string) => {
    if (items.type === "object" && items.properties) {
      return (
        <>
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
            JsonElementSelected === parent + `items` ? "active" : ""
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
        <h1 className="title">JSON Schema of the Selected Dataset</h1>
      </div>
      {jsonSchemaContext && (
        <div className="json-schema-container">
          <div className="json-schema">
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
