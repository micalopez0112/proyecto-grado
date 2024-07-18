import React, { useState } from "react";
import "./JsonSchema.css";
import { json as generateJsonSchema } from "generate-schema";

const Json = () => {
  // const jsonExample = {
  //   $schema: "http://json-schema.org/draft-04/schemaPersona",
  //   type: "object",
  //   properties: {
  //     id: {
  //       type: "int",
  //     },
  //     amenities: {
  //       type: "array",
  //       items: {
  //         type: "object",
  //         properties: {
  //           name: {
  //             type: "string",
  //           },
  //           age: {
  //             type: "integer",
  //           },
  //           hobbies: {
  //             type: "array",
  //             items: {
  //               type: "object",
  //               properties: {
  //                 hobbyName: {
  //                   type: "string",
  //                 },
  //                 skillLevel: {
  //                   type: "string",
  //                 },
  //               },
  //             },
  //           },
  //         },
  //         required: ["name", "age"],
  //       },
  //     },
  //     son: {
  //       type: "object",
  //       properties: {
  //         name: {
  //           type: "string",
  //         },
  //         age: {
  //           type: "integer",
  //         },
  //         hobbies: {
  //           type: "array",
  //           items: {
  //             type: "object",
  //             properties: {
  //               hobbyName: {
  //                 type: "string",
  //               },
  //               skillLevel: {
  //                 type: "string",
  //               },
  //             },
  //           },
  //         },
  //       },
  //       required: ["name", "age"],
  //     },
  //   },
  // };

  const [jsonInput, setJsonInput] = useState("");
  const [jsonSchema, setJsonSchema] = useState(null);

  const handleInputChange = (e) => {
    setJsonInput(e.target.value);
  };

  const handleGenerateSchema = () => {
    try {
      const jsonData = JSON.parse(jsonInput);
      const schema = generateJsonSchema(jsonData);
      setJsonSchema(schema);
    } catch (error) {
      console.error("Invalid JSON input");
      setJsonSchema(null);
    }
  };

  const renderProperties = (properties) => {
    return Object.entries(properties).map(([key, value]) => {
      if (value.type === "object" && value.properties) {
        return (
          <div className="property-box" key={key}>
            <div className="json-elem">
              <strong>{key}:</strong> object
            </div>

            <div className="object-properties">
              {renderProperties(value.properties)}
            </div>
          </div>
        );
      }
      if (value.type === "array" && value.items) {
        return (
          <div className="property-box" key={key}>
            <div className="json-elem">
              <strong>{key}:</strong> array
            </div>

            <div className="object-properties">
              {renderArrayItems(value.items)}
            </div>
          </div>
        );
      }
      return (
        <div className="property-box" key={key}>
          <div className="json-elem">
            <strong>{key}:</strong> {value.type}
          </div>
        </div>
      );
    });
  };

  const renderArrayItems = (items) => {
    if (items.type === "object" && items.properties) {
      return (
        <>
          <div className="json-elem">
            <strong>items:</strong> object
          </div>
          <div className="object-properties">
            {renderProperties(items.properties)}
          </div>
        </>
      );
    }
    return (
      <>
        <div className="json-elem">
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
          rows={10}
          cols={100}
          value={jsonInput}
          onChange={handleInputChange}
          placeholder="Enter JSON here"
        />
        <br />
        <button onClick={handleGenerateSchema}>Generate Schema</button>
      </div>
      {jsonSchema && (
        <div className="json-schema-container">
          {renderProperties(jsonSchema.properties)}
        </div>
      )}
    </div>
  );
};

export default Json;
