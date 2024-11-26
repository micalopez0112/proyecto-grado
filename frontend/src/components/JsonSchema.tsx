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
    e.stopPropagation();
    console.log("Obj. elem. selected: ", element);
    setJsonElementSelected(element);
  };

  const handleClickSimpleProperty = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string,
    type: string
  ) => {
    e.stopPropagation();
    setJsonElementSelected(element + "_key#" + type);
    console.log("Simp. elem. selected: " + element + "_key#" + type);
  };

  const handleClickArrayProperty = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string
  ) => {
    e.stopPropagation();
    setJsonElementSelected(element + "_key#array");
    console.log("Array elem. selected: " + element + "_key#array");
  };

  const renderProperties = (
    properties: Record<string, JsonSchemaProperty>,
    parent: string
  ) => {
    if (parent === "") {
      return (
        <div>
          <div className="property-box" key={"rootObject"}>
            <div
              className={`json-elem ${
                JsonElementSelected === "rootObject_value" ? "active" : ""
              }`}
              onClick={
                (e) => handleClickElement(e, "rootObject_value") //se tiene que mapear a class
              }
            >
              <strong>rootObject:</strong>
            </div>
            <div className="object-properties">
              {renderProperties(properties, "rootObject")}
            </div>
          </div>
        </div>
      );
    } else {
      return Object.entries(properties).map(([key, value]) => {
        if (value.type === "object" && value.properties) {
          const elementKey = parent ? `${parent}-${key}` : key;

          const fullKey = `${elementKey}_key#${value.type}`;

          console.log("fullKey ", fullKey);

          return (
            <div className="property-box" key={key}>
              <div
                className={`json-elem ${
                  JsonElementSelected === parent + "-" + key + "_key"
                    ? "active"
                    : ""
                }`}
                onClick={(e) =>
                  handleClickElement(
                    e,
                    parent ? parent + "-" + key + "_key" : key + "_key"
                  )
                }
              >
                <strong>{key}:</strong>
              </div>

              <div
                key={key + "_value"}
                className={`json-elem object-box ${
                  JsonElementSelected ===
                  (parent ? parent + "-" + key + "_value" : key + "_value")
                    ? "active"
                    : ""
                }`}
                onClick={(e) =>
                  handleClickElement(
                    e,
                    parent ? parent + "-" + key + "_value" : key + "_value"
                  )
                }
              >
                <strong>object</strong>
                <div className="object-properties">
                  {renderProperties(
                    value.properties,
                    parent ? parent + "-" + key : key
                  )}
                </div>
              </div>
            </div>
          );
        }
        if (value.type === "array" && value.items) {
          return (
            <div className="property-box" key={key}>
              <div
                className={`json-elem ${
                  JsonElementSelected ===
                  (parent ? parent + "-" + key + "_key#array" : key)
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
          <div className="object-property-box" key={key}>
            <div
              className={`json-elem ${
                JsonElementSelected ===
                (parent ? parent + "-" + key + "_key#" + value.type : key)
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
      });
    }
  };

  const renderArrayItems = (items: JsonSchemaProperty, parent: string) => {
    if (items.type === "object" && items.properties) {
      return (
        <>
          <div
            key={parent + "_value"}
            className={`json-elem array-box ${
              JsonElementSelected ===
              (parent ? parent + "_value" : parent + "_value")
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleClickElement(
                e,
                parent ? parent + "_value" : parent + "_value"
              )
            }
          >
            <strong>array items: object</strong>

            <div className="object-properties">
              {renderProperties(items.properties, parent)}
            </div>
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
