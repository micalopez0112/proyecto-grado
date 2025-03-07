import React, { useEffect, useState, useRef } from "react";
import { useDataContext } from "../../context/context.tsx";
import { useNavigate, useParams } from "react-router-dom";
import { OntologyDataType } from "../../types";
import { uploadOntology, getJsonSchema } from "../../services/mapsApi.ts";
import { Spinner } from "../../components/Spinner/Spinner.tsx";
import { toast } from "react-toastify";

const OntologySelectScreen = () => {
  const {
    collectionPath,
    externalFlow,
    externalDatasetId,
    setontologyDataContext,
    setcurrentOntologyId,
    clearMappings,
    setJsonSchemaContext,
  } = useDataContext();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [idSelectedOnto, setIdSelectedOnto] = useState<string>("");
  const [nextScreen, setNextScreen] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
  const [uriValue, setUriValue] = useState<string>("");
  const { collection_name } = useParams<{ collection_name?: string }>();
  const [loading, setLoading] = useState<boolean>(false);

  const handleOptionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedMethod(event.target.value);
  };
  useEffect(() => {
    //limpiar contexto de mappings
    clearMappings();
    if (collection_name) {
      //
      //Para codificar el path y pasarlo como parametro
      // const filePath = "C:/collections/dataset.json";
      // const encodedPath = encodeURIComponent(filePath);
      // navigate(`/OntologySelect/${encodedPath}`);

      //Para decodificar el path y obtener el nombre de la colección
      // const decodedPath = decodeURIComponent(collection_name);
      // console.log("Decoded path:", decodedPath);
      console.log("##Collection name from path##: ", collection_name);
    }
    // const retrieveOntologies = async () =>{
    //     const ontologies = await fetchOntologies();
    //     if(ontologies){
    //         console.log("Ontologies: ",ontologies);
    //         setOntologies(ontologies.data);
    //     }
    // }
    // retrieveOntologies();

    if (externalFlow) {
      console.log("#External Flow en OntologySelect.tsx#");
      console.log("Collection path: ", collectionPath);
      console.log("External dataset id: ", externalDatasetId);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const fileExtension = files[0].name.split(".").pop()?.toLowerCase();
      if (fileExtension === "owl" || fileExtension === "rdf") {
        setSelectedFile(files[0]);
        setNextScreen(true);
      } else {
        toast.error("El archivo debe ser de tipo .owl o .rdf");
        return;
      }
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      let response;
      if (selectedMethod && selectedMethod === "file" && selectedFile) {
        response = await uploadOntology("FILE", selectedFile, "");
      } else if (selectedMethod && selectedMethod === "uri" && uriValue) {
        response = await uploadOntology("URI", undefined, uriValue);
        console.log("Ontologia desde el back", response);
      } else {
        toast.error("Please select an ontology");
        setLoading(false);
        return;
      }
      const ontologyData: OntologyDataType = response?.data.ontologyData;
      const ontologyId = response?.data.ontologyData.ontology_id;
      setcurrentOntologyId(ontologyId);
      setontologyDataContext(ontologyData);
      if (externalFlow) {
        //cargar schema a partir del collection path y el externalIdDataset
        //navegar a MappingSelect
        setLoading(true);
        //const filePath = "C:/Users/fncastro/Documents/GitHub/APP/proyecto-grado/backend/app/Coleccion_Películas/algo.json"
        const response = await getJsonSchema(collectionPath); //filepath
        const schema = response?.data;
        //setJsonSchema(schema);
        console.log("##GENERATED SCHEMA##", schema);
        setJsonSchemaContext(schema); //Check que se pase bien esto
        setLoading(false);
        navigate("/Mapping");
      } else navigate("/SchemaSelect");
    } catch (error) {
      const errorMessage = error.response.data.detail;
      toast.error("Failed on submit: " + errorMessage);
      console.log("error en handleSubmit: ", errorMessage);
      setLoading(false);
    }
  };

  const handleSelectOntology = (id: string) => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    setIdSelectedOnto(id);
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div style={styles.container}>
          <h1>Upload the domain ontology</h1>
          <div style={styles.selectHeader}>
            <p style={{ fontSize: "16px" }}>Upload method:</p>
            <div style={styles.checkboxContainer}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  gap: "20px",
                }}
              >
                <label>
                  <input
                    type="radio"
                    value="file"
                    checked={selectedMethod === "file"}
                    onChange={handleOptionChange}
                  />
                  File
                </label>
                <label>
                  <input
                    type="radio"
                    value="uri"
                    checked={selectedMethod === "uri"}
                    onChange={handleOptionChange}
                  />
                  URI
                </label>
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                }}
              >
                {selectedMethod === "file" && (
                  <input
                    style={{ fontSize: "16px" }}
                    type="file"
                    onChange={handleFileChange}
                    ref={fileInputRef}
                  ></input>
                )}
                {selectedMethod === "uri" && (
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
                      value={uriValue}
                      onChange={(e) => setUriValue(e.target.value)}
                    ></input>
                  </div>
                )}
                {/* <ToastContainer/> */}
              </div>
            </div>
          </div>
          <button className="button" onClick={handleSubmit}>
            Confirm selection
          </button>
        </div>
      )}
    </>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "20px",
    minHeight: "100vh",
  },
  selectHeader: {
    display: "flex",
    flexDirection: "column",
    padding: "10px",
    width: "800px",
  },
  checkboxContainer: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    border: "2px solid #000",
    borderRadius: "8px",
    padding: "20px",
  },
  title: {
    fontSize: "2em",
    color: "#000",
    marginBottom: "20px",
  },
  button: {
    padding: "10px 20px",
    fontSize: "1em",
    color: "#fff",
    backgroundColor: "#000",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    marginBottom: "20px",
  },
  dashboard: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
    gap: "10px",
    width: "100%",
    maxWidth: "800px",
    marginTop: "10px",
    maxHeight: "1000px",
    overflowY: "scroll",
  },
  ontologyCard: {
    backgroundColor: "#fff",
    padding: "15px",
    borderRadius: "5px",
    boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
    color: "#000",
    cursor: "pointer",
    transition: "background-color 0.3s ease",
    wordBreak: "break-word",
  },
};

export default OntologySelectScreen;
