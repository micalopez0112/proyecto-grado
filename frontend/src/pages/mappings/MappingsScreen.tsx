import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchMappings } from "../../services/mapsApi.ts";
import MappingCard from "../../components/MappingCard.tsx";
import { Spinner } from "../../components/Spinner/Spinner.tsx";
import "./MappingsScreen.css";

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

  const handleDeleteMapping = (id: string) => {
    setMappings((prevMappings) =>
      prevMappings.filter((mapping) => mapping.id !== id)
    );
  };

  const filteredMappings = mappings.filter((mapping) =>
    mapping.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="mappings-list-container">
          <div className="mappings-title-container">
            <h1 className="mappings-list-title">Set of Mappings</h1>
          </div>
          <div className="input-button-container">
            <input
              type="text"
              placeholder="Search Set of Mappings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <button
              onClick={() => navigate("/OntologySelect")}
              className="button"
            >
              New Set of Mapping
            </button>
          </div>
          {filteredMappings.length > 0 ? (
            <div className="dashboard">
              {filteredMappings.map((mapping) => (
                <MappingCard
                  key={mapping.id}
                  id={mapping.id}
                  name={mapping.name}
                  onClickCallback={onClickMappingCard}
                  onDeleteCallback={handleDeleteMapping}
                  style={styles.mappingCard}
                  includeTrash={true}
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
  mappingCard: {
    backgroundColor: "rgb(239 239 239)",
    padding: "15px",
    borderRadius: "5px",
    boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
    color: "#000",
    cursor: "pointer",
    display: "flex",
    justifyContent: "space-between",
  },
};

export default MappingsScreen;
