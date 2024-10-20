import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { evaluateMapping, getMapping } from "../../../services/mapsApi.ts";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import { useDataContext } from "../../../context/context.tsx";
import { FaArrowRightLong } from "react-icons/fa6";
import "./SelectMappingsEvaluate.css";

const SYNTCTATIC_ACCURACY = "syntactic_accuracy";
const QUALITY_RULES = [SYNTCTATIC_ACCURACY];

const SelectMappingsEvaluate = () => {
  const navigate = useNavigate();
  const { mappings, setMappings } = useDataContext();

  const location = useLocation();
  const mappingId = location.state?.mappingId;
  const ruleId = location.state?.ruleId;

  const [mappingName, setMappingName] = useState<string>("");
  const [selectedMappings, setSelectedMappings] = useState<Record<string, any>>(
    {}
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [allSelected, setAllSelected] = useState<boolean>(false); // New state for tracking if all mappings are selected

  useEffect(() => {
    const getMappingData = async () => {
      if (mappingId) {
        setLoading(true);
        try {
          const response = await getMapping(mappingId, true);
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

  const handleToggleMapping = (key: string, mappingElement: any) => {
    setSelectedMappings((prev) => {
      const updated = { ...prev };
      if (updated[key]) {
        delete updated[key];
      } else {
        updated[key] = mappingElement;
      }
      return updated;
    });
  };

  useEffect(() => {
    console.log("Selected mappings updated: ", selectedMappings);
  }, [selectedMappings]);

  // New function to handle selecting/deselecting all mappings
  const handleSelectAllMappings = () => {
    if (!allSelected) {
      const allMappings: Record<string, any> = {};
      Object.keys(mappings).forEach((key) => {
        allMappings[key] = mappings[key];
      });
      setSelectedMappings(allMappings);
    } else {
      setSelectedMappings({});
    }
    setAllSelected(!allSelected); // Toggle between selecting and deselecting all
  };

  const handleEvaluateSelectedMappings = async () => {
    const response = await evaluateMapping(
      SYNTCTATIC_ACCURACY,
      mappingId,
      selectedMappings
    );

    navigate("/EvaluateMappings", {
      state: {
        selectedMappings: selectedMappings,
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
                {/* Add the Select All button */}
                <button
                  className="button select-all"
                  onClick={handleSelectAllMappings}
                >
                  {allSelected ? "Deselect All" : "Select All"}
                </button>

                {Object.keys(mappings).map((key) => (
                  <div className="mapping" key={key}>
                    <ul className="list-container">
                      {mappings[key].map((element, index) => (
                        <li key={index} className="list-elem-evaluate">
                          <div className="value-wrapper-evaluation">
                            <div className="key-title">JSON schema value</div>
                            <div className="key-text" title={key}>
                              {key}
                            </div>
                          </div>

                          <FaArrowRightLong className="arrow-icon" />

                          <div className="value-wrapper-evaluation">
                            <div className="element-title">
                              Ontology element
                            </div>
                            <div className="element-name" title={element.name}>
                              {element.name}
                            </div>
                          </div>

                          <input
                            type="checkbox"
                            checked={!!selectedMappings[key]} // Update to reflect selected mappings
                            onChange={() =>
                              handleToggleMapping(key, mappings[key])
                            }
                          />
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}

                <button
                  className="button success"
                  onClick={handleEvaluateSelectedMappings}
                  disabled={Object.keys(selectedMappings).length === 0}
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
