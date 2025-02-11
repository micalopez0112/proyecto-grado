export interface JsonSchemaProperty {
  type: string;
  properties?: Record<string, JsonSchemaProperty>;
  items?: JsonSchemaProperty;
  anyOf?: JsonSchemaProperty[];
}
export interface JsonSchema {
  type: string;
  properties: Record<string, JsonSchemaProperty>;
}
