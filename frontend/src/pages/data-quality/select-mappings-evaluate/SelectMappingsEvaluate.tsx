import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { evaluateMapping, getMapping } from "../../../services/mapsApi.ts";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import { useDataContext } from "../../../context/context.tsx";
import { FaArrowRightLong } from "react-icons/fa6";
import "./SelectMappingsEvaluate.css";
import { JsonSchemaProperty } from "../../../types/JsonSchema.ts";

const SYNTCTATIC_ACCURACY = "syntactic_accuracy";
const QUALITY_RULES = [SYNTCTATIC_ACCURACY];

const SelectMappingsEvaluate = () => {
  const navigate = useNavigate();
  const {
    mappings,
    setcurrentOntologyId,
    setontologyDataContext,
    setMappings,
    setJsonSchemaContext,
    jsonSchemaContext,
    setMappingProcessId,
    mappingProcessId,
  } = useDataContext();

  const location = useLocation();
  const mappingId = location.state?.mappingId;
  const ruleId = location.state?.ruleId;

  const [mappingName, setMappingName] = useState<string>("");
  const [selectedMappings, setSelectedMappings] = useState<Record<string, any>>(
    {}
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [allSelected, setAllSelected] = useState<boolean>(false);

  const getSimpleMappings = () => {
    return Object.keys(mappings).filter(
      (key) =>
        key.endsWith("#string") ||
        key.endsWith("#number") ||
        key.endsWith("#boolean")
    );
  };

  useEffect(() => {
    const getMappingData = async () => {
      if (mappingId) {
        setLoading(true);
        try {
          const response = await getMapping(mappingId);
          if (response) {
            const { mapping_name, mapping, schema, ontology } = response.data;
            setMappingProcessId(mappingId);
            setMappings(mapping);
            setJsonSchemaContext(schema);
            setcurrentOntologyId(ontology.ontology_id);
            setontologyDataContext(ontology);
            setMappingName(mapping_name);
          }
        } catch (error) {
          console.error("Error in getMappingData", error);
        }
        setLoading(false);
      }
    };
    getMappingData();
  }, [mappingId]);

  useEffect(() => {
    const simpleMappings = getSimpleMappings();
    const allSimpleSelected = simpleMappings.every((key) =>
      selectedMappings.hasOwnProperty(key)
    );
    setAllSelected(allSimpleSelected);
  }, [selectedMappings, mappings]);

  const handleToggleMapping = (
    key: string,
    mappingElement: any,
    e: React.MouseEvent<HTMLDivElement>
  ) => {
    e.stopPropagation();
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

  const handleSelectAllMappings = () => {
    if (!allSelected) {
      const simpleMappings = getSimpleMappings();
      const allMappings: Record<string, any> = {};
      simpleMappings.forEach((key) => {
        allMappings[key] = mappings[key];
      });
      setSelectedMappings(allMappings);
    } else {
      setSelectedMappings({});
    }
  };

  const handleEvaluateSelectedMappings = async () => {
    setLoading(true);
    try {
      const response = await evaluateMapping(
        SYNTCTATIC_ACCURACY,
        mappingId,
        selectedMappings
      );

      if (response) {
        navigate("/EvaluateMappings", {
          state: {
            selectedMappings,
            ruleId,
            validationResults: response.data,
          },
        });
      }
    } catch (error) {
      console.error("Error evaluating mappings:", error);
    } finally {
      setLoading(false);
    }
  };

  const renderProperties = (
    properties: Record<string, JsonSchemaProperty>,
    parent: string
  ) => {
    if (parent === "") {
      return (
        <div>
          <div className="property-box" key={"rootObject"}>
            <div className="json-elem disabled">
              <strong>rootObject:</strong>
            </div>
            <div className="object-properties">
              {renderProperties(properties, "rootObject")}
            </div>
          </div>
        </div>
      );
    }

    return Object.entries(properties).map(([key, value]) => {
      let elementKey = parent ? `${parent}-${key}` : key;
      const fullKey = `${elementKey}_key#${value.type}`;
      const isMapped = !!mappings[fullKey];
      const mappingInfo = isMapped ? mappings[fullKey] : null;
      const isActive = !!selectedMappings[fullKey];

      if (value.type === "object" && value.properties) {
        const elementValue = elementKey + "_value";
        const isMappedObjectValue = !!mappings[elementValue];
        const mappingInfoValue = isMappedObjectValue
          ? mappings[elementValue]
          : null;

        return (
          <div className="property-box" key={key}>
            <div className="json-elem disabled">
              <strong>{key}:</strong> object
            </div>
            <div className="object-properties">
              {renderProperties(value.properties, `${parent}-${key}`)}
            </div>
          </div>
        );
      }

      if (value.type === "array" && value.items) {
        return (
          <div className="property-box" key={key}>
            <div
              className={`json-elem ${isMapped ? "clickable" : "disabled"} ${
                isActive ? "active" : ""
              }`}
              onClick={(e) =>
                isMapped && handleToggleMapping(fullKey, mappingInfo, e)
              }
            >
              <strong>{key}:</strong> array
            </div>
          </div>
        );
      }

      return (
        <div className="property-box mapping-box" key={key}>
          <div
            className={`json-elem ${isMapped ? "clickable" : "disabled"} ${
              isActive ? "active" : ""
            }`}
            onClick={(e) =>
              isMapped && handleToggleMapping(fullKey, mappingInfo, e)
            }
          >
            <strong>{key}:</strong> {value.type}
          </div>
        </div>
      );
    });
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="container">
          <h1 className="title-section">
            Select schema values to evaluate data
          </h1>
          <div className="select-mappings-container">
            {mappings && (
              <div className="mappings">
                <button
                  className="button select-all"
                  onClick={handleSelectAllMappings}
                >
                  {allSelected ? "Deselect All" : "Select All"}
                </button>
                {jsonSchemaContext && (
                  <div className="json-schema-container">
                    <div className="json-schema">
                      {jsonSchemaContext.properties &&
                        renderProperties(jsonSchemaContext.properties, "")}
                    </div>
                  </div>
                )}
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
