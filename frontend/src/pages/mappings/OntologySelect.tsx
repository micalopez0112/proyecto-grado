import React, { useEffect, useState, useRef } from "react";
import { useDataContext } from "../../context/context.tsx";
import { useNavigate, useParams } from "react-router-dom";
import { OntologyDataType } from "../../types";
import { uploadOntology, getJsonSchema } from "../../services/mapsApi.ts";
import { Spinner } from "../../components/Spinner/Spinner.tsx";
import { toast } from "react-toastify";
import InfoModal from "../../components/InfoModal/InfoModal.tsx";
import BackButton from "../../components/BackButton/BackButton.tsx";

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
        const response = await getJsonSchema(collectionPath);
        const schema = response?.data;
        setJsonSchemaContext(schema);
        setLoading(false);
        navigate("/Mapping");
      } else navigate("/SchemaSelect");
    } catch (error) {
      const errorMessage = error.response.data.detail;
      toast.error("Failed on submit: " + errorMessage);
      setLoading(false);
    }
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div style={styles.container}>
          <div className="title-info">
            <BackButton />
            <h1>Upload the domain ontology</h1>
            <InfoModal
              text={
                "On this screen you can select the Domain Ontology that will be used as Context."
              }
            />
          </div>
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
};

export default OntologySelectScreen;
