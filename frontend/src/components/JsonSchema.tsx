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
    if (element === JsonElementSelected) {
      setJsonElementSelected("");
    } else {
      setJsonElementSelected(element);
    }
  };

  const handleClickSimpleProperty = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string,
    type: string
  ) => {
    e.stopPropagation();
    element = element + "?key#" + type;
    if (JsonElementSelected === element) {
      setJsonElementSelected("");
    } else {
      setJsonElementSelected(element);
    }
    console.log("Simp. elem. selected: " + element);
  };

  const handleClickArrayProperty = (
    e: React.MouseEvent<HTMLDivElement>,
    element: string
  ) => {
    e.stopPropagation();
    element = element + "?key#array";
    if (JsonElementSelected === element) {
      setJsonElementSelected("");
    } else {
      setJsonElementSelected(element);
    }
    console.log("Array elem. selected: " + element);
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
                JsonElementSelected === "rootObject?value" ? "active" : ""
              }`}
              onClick={
                (e) => handleClickElement(e, "rootObject?value") //se tiene que mapear a class
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

          const fullKey = `${elementKey}?key#${value.type}`;

          console.log("fullKey ", fullKey);

          return (
            <div className="property-box" key={key}>
              <div
                className={`json-elem ${
                  JsonElementSelected === parent + "-" + key + "?key"
                    ? "active"
                    : ""
                }`}
                onClick={(e) =>
                  handleClickElement(
                    e,
                    parent ? parent + "-" + key + "?key" : key + "?key"
                  )
                }
              >
                <strong>{key}:</strong>
              </div>

              <div
                key={key + "?value"}
                className={`json-elem object-box ${
                  JsonElementSelected ===
                  (parent ? parent + "-" + key + "?value" : key + "?value")
                    ? "active"
                    : ""
                }`}
                onClick={(e) =>
                  handleClickElement(
                    e,
                    parent ? parent + "-" + key + "?value" : key + "?value"
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
          if (value.items.anyOf) {
            console.log("anyOf array", value.items.anyOf);
          }
          return (
            <div className="property-box" key={key}>
              <div
                className={`json-elem ${
                  JsonElementSelected ===
                  (parent ? parent + "-" + key + "?key#array" : key)
                    ? "active"
                    : ""
                } ${value.items.anyOf ? "disabled" : ""}`}
                onClick={(e) => handleClickArrayProperty(e, parent + "-" + key)}
              >
                <strong>{key}:</strong> array
              </div>
              {value.items.anyOf ? (
                value.items.anyOf.map((element) => {
                  console.log("Element", element);
                  return (
                    <div className="object-properties">
                      {renderArrayItemsAnyOf(element, parent + "-" + key)}
                    </div>
                  );
                })
              ) : (
                <div className="object-properties">
                  {renderArrayItems(value.items, parent + "-" + key)}
                </div>
              )}
            </div>
          );
        }
        return (
          <div className="object-property-box" key={key}>
            <div
              className={`json-elem ${
                JsonElementSelected ===
                (parent ? parent + "-" + key + "?key#" + value.type : key)
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
            key={parent + "?value"}
            className={`json-elem array-box ${
              JsonElementSelected ===
              (parent ? parent + "?value" : parent + "?value")
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleClickElement(
                e,
                parent ? parent + "?value" : parent + "?value"
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
          className={`json-elem ${
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

  const renderArrayItemsAnyOf = (items: JsonSchemaProperty, parent: string) => {
    if (items.type === "object" && items.properties) {
      return (
        <>
          <div
            key={parent + "?value"}
            className={`json-elem array-box disabled `}
            onClick={(e) =>
              handleClickElement(
                e,
                parent ? parent + "?value" : parent + "?value"
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
        {Array.isArray(items.type) ? (
          items.type.map((element) => {
            return (
              <div
                className={`json-elem array-box disabled`}
                onClick={(e) =>
                  console.log("clicked array item, doesn´t do anything")
                }
              >
                <strong>array items:</strong> {element}
              </div>
            );
          })
        ) : (
          <div
            className={`json-elem array-box disabled`}
            onClick={(e) =>
              console.log("clicked array item, doesn´t do anything")
            }
          >
            <strong>array items:</strong> {items.type}
          </div>
        )}
      </>
    );
  };

  return (
    <div className="container">
      <div className="title-wrapper">
        <h1 className="title">JSON Schema of the selected dataset</h1>
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
