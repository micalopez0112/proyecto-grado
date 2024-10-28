import React, { useEffect, useState, useRef } from "react";
import { useDataContext } from "../../context/context.tsx";
import { useNavigate } from "react-router-dom";
import { OntologyDataType } from "../../types";
import { uploadOntology } from "../../services/mapsApi.ts";
import { Spinner } from "../../components/Spinner/Spinner.tsx";

const OntologySelectScreen = () => {
  const [ontologies, setOntologies] = useState<
    Array<{ id: string; type: string; file: string; uri: string }>
  >([]);
  const { ontologyDataContext, setontologyDataContext, setcurrentOntologyId } =
    useDataContext();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [idSelectedOnto, setIdSelectedOnto] = useState<string>("");
  const [nextScreen, setNextScreen] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
  const [uriValue, setUriValue] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const { mappings, clearMappings } = useDataContext();

  const handleOptionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedMethod(event.target.value);
  };

  useEffect(() => {
    //limpiar contexto de mappings
    clearMappings();
    // const retrieveOntologies = async () =>{
    //     const ontologies = await fetchOntologies();
    //     if(ontologies){
    //         console.log("Ontologies: ",ontologies);
    //         setOntologies(ontologies.data);
    //     }
    // }
    // retrieveOntologies();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const fileExtension = files[0].name.split(".").pop()?.toLowerCase();
      if (fileExtension === "owl" || fileExtension === "rdf") {
        setSelectedFile(files[0]);
        setNextScreen(true);
      } else {
        alert("El archivo debe ser de tipo .owl o .rdf");
        return;
      }
    }
  };

  const handleSubmit = async () => {
    console.log("a");
    try {
      setLoading(true);
      if (selectedMethod && selectedMethod === "file" && selectedFile) {
        const response = await uploadOntology("FILE", selectedFile, "");
        console.log("Ontologia desde el back", response);
        const ontologyData: OntologyDataType = response?.data.ontologyData;
        const ontologyId = response?.data.ontologyData.ontology_id;
        setcurrentOntologyId(ontologyId);
        setontologyDataContext(ontologyData);
      } else if (selectedMethod && selectedMethod === "uri" && uriValue) {
        //get ontology via URI
        //get ontology data from backend
        //setcurrentOntologyId(idSelectedOnto);
        const response = await uploadOntology("URI", undefined, uriValue);
        console.log("Ontologia desde el back", response);
        const ontologyData: OntologyDataType = response?.data.ontologyData;
        const ontologyId = response?.data.ontologyData.ontology_id;
        setcurrentOntologyId(ontologyId);
        setontologyDataContext(ontologyData);
      }
      setLoading(false);
      navigate("/SchemaSelect");
    } catch (error) {
      console.log("error en handleSubmit: ", error);
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
          <h1>Seleccione la ontología de contexto</h1>
          <button className="button" onClick={handleSubmit}>
            Confirmar selección
          </button>
          <div style={styles.selectHeader}>
            <p
              style={{
                display: "flex",
                alignItems: "flex-start",
                fontSize: "18px",
              }}
            >
              Cargar la ontología:
            </p>

            <div style={styles.checkboxContainer}>
              <p style={{ fontSize: "16px" }}>Método de carga:</p>
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
                  Archivo
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
                  paddingTop: "10px",
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
              </div>
            </div>
          </div>
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
    backgroundColor: "#f0f0f0",
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
