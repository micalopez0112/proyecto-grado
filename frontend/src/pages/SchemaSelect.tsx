import React,{useState} from 'react'
import { useDataContext } from '../context/context.tsx';
import { JsonSchema, JsonSchemaProperty } from "../types";
import { json as generateJsonSchema } from "generate-schema";
import { useNavigate } from 'react-router-dom';

const SchemaSelect = () => {
    
    const [jsonInput, setJsonInput] = useState<string>("");
    const [jsonSchema, setJsonSchema] = useState<JsonSchema | null>(null);
    const {setJsonSchemaContext} = useDataContext();

    const navigate = useNavigate();

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setJsonInput(e.target.value);
      };

      const handleGenerateSchema = () => {
        try {
          const jsonData = JSON.parse(jsonInput);
          const schema = generateJsonSchema(jsonData);
          console.log("##GENERATED SCHEMA##", schema);
          setJsonSchema(schema);
          setJsonSchemaContext(schema);
          navigate('/Mappings');
        } catch (error) {
          console.error("Invalid JSON input");
          setJsonSchema(null);
        }
      };
    
    return (
        <div style={styles.container}>
            <h1>Schema Select</h1>
            <div style={{display:'flex',flexDirection:'column',}}>
            <span style={{fontFamily:'Roboto',fontSize:'25px', marginBottom:'10px'}}>JSON to JSON Schema Converter</span>
                <textarea
                rows={20}
                cols={35}
                value={jsonInput}
                onChange={handleInputChange}
                placeholder="Enter JSON here"
                />
            </div>
            <div style={{
          display: "flex",
          justifyContent: "center",
          marginTop: "10px",
        }}>
        <button
            className='button' 
            onClick={handleGenerateSchema}>
                Generate Schema
        </button>
        </div>
        </div>
    )
}



const styles: { [key: string]: React.CSSProperties } = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '20px',
        backgroundColor: '#f0f0f0',
        minHeight: '100vh',
      },
      inputWrapper:{

      }

}

export default SchemaSelect;