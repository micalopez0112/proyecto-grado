import React, { useState } from "react";
import { JsonSchema } from "../../types";
import { useDataContext } from "../../context/context.tsx";
import { useNavigate } from "react-router-dom";
import { getJsonSchema } from "../../services/mapsApi.ts";
import { Spinner } from "../../components/Spinner/Spinner.tsx";

const SchemaSelect = () => {
  const [filePath, setFilePath] = useState<string>("");
  const [jsonInput, setJsonInput] = useState<string>("");
  const [jsonSchema, setJsonSchema] = useState<JsonSchema | null>(null);
  const { setJsonSchemaContext, setCollectionPath } = useDataContext();
  const [loading, setLoading] = useState<boolean>(false);

  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const fileExtension = files[0].name.split(".").pop()?.toLowerCase();
      if (fileExtension === "json") {
        setFile(files[0]);
      } else {
        alert("The Collection File must be of type .json");
        return;
      }
    }
  }

  const handleGenerateSchema = async () => {
    try {
      if(filePath !== ""){
        //CHECK FILEPATH SIZE > 0
        console.log("##File path: ", filePath);
        setLoading(true);
        //const filePath = "C:/Users/fncastro/Documents/GitHub/APP/proyecto-grado/backend/app/Coleccion_Películas/algo.json"
        const response = await getJsonSchema(filePath);//filepath
        //handle error al abrir el archivo
        const schema = response?.data;
        setJsonSchema(schema);
        console.log("##GENERATED SCHEMA##", schema);
        setJsonSchemaContext(schema);
        setCollectionPath(filePath); //Check que se pase bien esto
        navigate("/Mapping");
        setLoading(false);
      }
    } catch (error) {
      setFilePath("");
      console.error("Invalid JSON input");
      setJsonSchema(null);
      alert("Something went wrong uploading the collection file");
      setLoading(false);
    }
  };

  return (
    <>
    {loading ? (
      <Spinner />
    ):(
    <div style={styles.container}>
      <h1>Select Dataset</h1>
      <div style={styles.selectHeader}>
      <p style={{
                margin: "10px",
                display: "flex",
                alignItems: "flex-start",
                fontSize: "18px",
              }}>
        Upload the dataset from file system:
      </p>
      <div
      style={{
        display:"flex",
        flexDirection:"column",
        border: "2px solid rgb(0,0,0)",
        borderRadius: "8px",
        padding: "10px",
        
      }}>
        <input
          style={{ fontSize: "16px", paddingBottom: "10px" }}
          type="file"
          onChange={handleFileChange}
        >
        </input>
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            gap: "8px",
          }}
        >
          <label style={{ fontSize: "16px" }}>URI:</label>
          <input
            style={{}}
            type="text"
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
          ></input>
        </div>
        <button className="button" onClick={handleGenerateSchema}
          disabled={filePath === ""} >
          Confirm Dataset and Generate Schema
        </button>
        </div>
      </div>

    </div>)}
    </>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "20px",
    backgroundColor: "#f0f0f0",
    minHeight: "100vh",
  },
  inputWrapper: {},
  selectHeader:{
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "800px",
  },
};

export default SchemaSelect;
