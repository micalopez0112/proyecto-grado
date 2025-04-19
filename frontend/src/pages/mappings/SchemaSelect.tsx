import React, { useState } from "react";
import { JsonSchema } from "../../types";
import { useDataContext } from "../../context/context.tsx";
import { useNavigate } from "react-router-dom";
import { getJsonSchema } from "../../services/mapsApi.ts";
import { Spinner } from "../../components/Spinner/Spinner.tsx";
import { toast } from "react-toastify";
import InfoModal from "../../components/InfoModal/InfoModal.tsx";
import BackButton from "../../components/BackButton/BackButton.tsx";

const SchemaSelect = () => {
  const [filePath, setFilePath] = useState<string>("");
  const [jsonSchema, setJsonSchema] = useState<JsonSchema | null>(null);
  const { setJsonSchemaContext, setCollectionPath } = useDataContext();
  const [loading, setLoading] = useState<boolean>(false);

  const navigate = useNavigate();

  const handleGenerateSchema = async () => {
    try {
      if (filePath !== "") {
        setLoading(true);
        const response = await getJsonSchema(filePath);
        const schema = response?.data;
        setJsonSchema(schema);
        setJsonSchemaContext(schema);
        setCollectionPath(filePath);
        navigate("/Mapping");
        setLoading(false);
      } else {
        toast.error("Please introduce a valid path to load the dataset");
        setLoading(false);
        return;
      }
    } catch (error) {
      setFilePath("");
      toast.error(
        "Invalid path, please introduce a valid one to load the dataset"
      );
      setJsonSchema(null);
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
            <h1>Upload dataset</h1>
            <InfoModal
              text={
                "The dataset must be in JSON format. It serves as the source dataset from which you can define mappings against the previously loaded domain ontology."
              }
            />
          </div>
          <div style={styles.selectHeader}>
            <p
              style={{
                marginBottom: "8px",
                display: "flex",
                alignItems: "flex-start",
                fontSize: "18px",
              }}
            >
              Provide a local path to load the dataset from:
            </p>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                border: "2px solid rgb(0,0,0)",
                borderRadius: "8px",
                padding: "10px",
                alignItems: "center",
              }}
            >
              <div
                style={{
                  display: "flex",
                  flexDirection: "row",
                  justifyContent: "center",
                  gap: "12px",
                }}
              >
                <label style={{ fontSize: "18px" }}>Path:</label>
                <input
                  style={{}}
                  type="text"
                  value={filePath}
                  onChange={(e) => setFilePath(e.target.value)}
                ></input>
              </div>
            </div>
          </div>
          <button
            className="button"
            onClick={handleGenerateSchema}
            disabled={filePath === ""}
          >
            Confirm dataset and generate schema
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
  inputWrapper: {},
  selectHeader: {
    display: "flex",
    flexDirection: "column",
    width: "800px",
  },
};

export default SchemaSelect;
