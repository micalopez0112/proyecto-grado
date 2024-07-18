import React, { useState } from "react";
import "./JsonSchema.css";
import { json as generateJsonSchema } from "generate-schema";

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

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setJsonInput(e.target.value);
  };

  const handleGenerateSchema = () => {
    try {
      const jsonData = JSON.parse(jsonInput);
      //ver tipo de la siguiente linea
      const schema = generateJsonSchema(jsonData) as unknown as JsonSchema;
      setJsonSchema(schema);
    } catch (error) {
      console.error("Invalid JSON input");
      setJsonSchema(null);
    }
  };

  const renderProperties = (properties: Record<string, JsonSchemaProperty>) => {
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

  const renderArrayItems = (items: JsonSchemaProperty) => {
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
          rows={50}
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
          <div className="json-schema">
            <h2>Generated JSON Schema</h2>
            <pre className="json-schema">
              {JSON.stringify(jsonSchema, null, 2)}
            </pre>
          </div>

          {renderProperties(jsonSchema.properties)}
        </div>
      )}
    </div>
  );
};

export default Json;
