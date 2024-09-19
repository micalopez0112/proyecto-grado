import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchMappings } from "../../services/mapsApi.ts";
import MappingCard from "../../components/MappingCard.tsx";
import { Spinner } from "../../components/Spinner/Spinner.tsx";

const MappingsScreen = () => {
  const navigate = useNavigate();
  const [mappings, setMappings] = useState<Array<{ id: string; name: string }>>(
    []
  );
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const retrieveMappings = async () => {
      setLoading(true);
      const mappings = await fetchMappings();
      console.log("Mappings: ", mappings);
      //setMappings(mappings);
      if (mappings) setMappings(mappings.data);
      setLoading(false);
    };
    retrieveMappings();
  }, []);

  const onClickMappingCard = (id: string) => {
    navigate("/Mapping", { state: { mappingId: id } });
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div style={styles.container}>
          <div style={styles.mappingsTitleContainer}>
            <h1 style={styles.title}>Mappings</h1>
            <button
              onClick={() => navigate("/OntologySelect")}
              style={styles.button}
            >
              Nuevo Mapping
            </button>
          </div>
          {mappings && (
            <div style={styles.dashboard}>
              {mappings.map((mapping) => (
                <MappingCard
                  key={mapping.id}
                  id={mapping.id}
                  name={mapping.name}
                  onClickCallback={onClickMappingCard}
                  style={styles.mappingCard}
                />
              ))}
            </div>
          )}
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
    position: "absolute",
    right: "282px",
    top: "50px",
  },
  dashboard: {
    display: "grid",
    gridTemplateColumns: "1fr",
    gap: "10px",
    width: "100%",
    maxWidth: "1000px",
  },
  mappingCard: {
    backgroundColor: "#fff",
    padding: "15px",
    borderRadius: "5px",
    boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
    color: "#000",
    cursor: "pointer",
    transition: "background-color 0.3s ease",
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
  },
  mappingsTitleContainer: {
    display: "flex",
  },
};

export default MappingsScreen;
