export interface JsonSchemaProperty {
  type: string;
  properties?: Record<string, JsonSchemaProperty>;
  items?: JsonSchemaProperty;
}
export interface JsonSchema {
  type: string;
  properties: Record<string, JsonSchemaProperty>;
}
