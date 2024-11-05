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
  const [searchTerm, setSearchTerm] = useState<string>("");

  useEffect(() => {
    const retrieveMappings = async () => {
      setLoading(true);
      const mappings = await fetchMappings();
      console.log("Mappings: ", mappings);
      if (mappings) setMappings(mappings.data);
      setLoading(false);
    };
    retrieveMappings();
  }, []);

  const onClickMappingCard = (id: string) => {
    navigate("/Mapping", { state: { mappingId: id } });
  };

  const filteredMappings = mappings.filter((mapping) =>
    mapping.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div style={styles.container}>
          <div style={styles.mappingsTitleContainer}>
            <h1 style={styles.title}>Set of Mappings</h1>
            <button
              onClick={() => navigate("/OntologySelect")}
              style={styles.button}
            >
              New Set of Mapping
            </button>
          </div>
          <input
            type="text"
            placeholder="Search Set of Mappings..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={styles.searchInput}
          />
          {filteredMappings.length > 0 ? (
            <div style={styles.dashboard}>
              {filteredMappings.map((mapping) => (
                <MappingCard
                  key={mapping.id}
                  id={mapping.id}
                  name={mapping.name}
                  onClickCallback={onClickMappingCard}
                  style={styles.mappingCard}
                />
              ))}
            </div>
          ) : (
            <p>No mappings found</p>
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
    backgroundColor: "#fff",
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
    top: 100,
  },
  searchInput: {
    width: "100%",
    maxWidth: "400px",
    padding: "10px",
    fontSize: "1em",
    marginBottom: "20px",
    border: "1px solid #ccc",
    borderRadius: "5px",
  },
  dashboard: {
    display: "grid",
    gridTemplateColumns: "1fr",
    gap: "10px",
    width: "100%",
    maxWidth: "1000px",
  },
  mappingCard: {
    backgroundColor: "rgb(239 239 239)",
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
