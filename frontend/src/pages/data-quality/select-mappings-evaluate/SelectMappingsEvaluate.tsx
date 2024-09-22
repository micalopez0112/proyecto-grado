import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getMapping } from "../../../services/mapsApi.ts";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import { useDataContext } from "../../../context/context.tsx";
import { FaArrowRightLong } from "react-icons/fa6";
import "./SelectMappingsEvaluate.css";

const SelectMappingsEvaluate = () => {
  const navigate = useNavigate();
  const { mappings, setMappings } = useDataContext();

  const location = useLocation();
  const mappingId = location.state?.mappingId;
  const ruleId = location.state?.ruleId;

  const [mappingName, setMappingName] = useState<string>("");
  const [selectedMappings, setSelectedMappings] = useState<Set<string>>(
    new Set()
  );
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const getMappingData = async () => {
      if (mappingId) {
        setLoading(true);
        try {
          const response = await getMapping(mappingId);
          if (response) {
            const { mapping_name, mapping } = response.data;
            setMappings(mapping);
            setMappingName(mapping_name);
          }
        } catch (error) {
          console.error("Error fetching mapping data:", error);
        }
        setLoading(false);
      }
    };
    getMappingData();
  }, [mappingId]);

  const handleToggleMapping = (key: string) => {
    setSelectedMappings((prev) => {
      const updated = new Set(prev);
      if (updated.has(key)) {
        updated.delete(key);
      } else {
        updated.add(key);
      }
      return updated;
    });
  };

  // Monitor the selected mappings
  useEffect(() => {
    console.log("Selected mappings updated: ", Array.from(selectedMappings));
  }, [selectedMappings]);

  const handleEvaluateSelectedMappings = () => {
    navigate("/EvaluateMappings", {
      state: {
        selectedMappings: Array.from(selectedMappings),
        ruleId: ruleId,
      },
    });
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="container">
          <h1 className="title-section">Select Mappings to Evaluate</h1>

          <div className="select-mappings-container">
            {mappings && (
              <div className="mappings">
                {Object.keys(mappings).map((key) => {
                  return (
                    <div className="mapping" key={key}>
                      <ul className="list-container">
                        {mappings[key].map((element, index) => (
                          <li key={index} className="list-elem">
                            <div className="value-wrapper">
                              <div className="key-title">JSON schema value</div>
                              <div className="key-text" title={key}>
                                {key}
                              </div>
                            </div>

                            <FaArrowRightLong className="arrow-icon" />

                            <div className="value-wrapper">
                              <div className="element-title">
                                Ontology element
                              </div>
                              <div
                                className="element-name"
                                title={element.name}
                              >
                                {element.name}
                              </div>
                            </div>

                            <input
                              type="checkbox"
                              onChange={() => handleToggleMapping(key)}
                            />
                          </li>
                        ))}
                      </ul>
                    </div>
                  );
                })}

                <button
                  className="button success"
                  onClick={handleEvaluateSelectedMappings}
                  disabled={selectedMappings.size === 0}
                >
                  Evaluate Selected Mappings
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default SelectMappingsEvaluate;
