import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { fetchMappings, getMapping } from "../../../services/mapsApi.ts";
import MappingCard from "../../../components/MappingCard.tsx";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import { useDataContext } from "../../../context/context.tsx";
import { FaArrowRightLong } from "react-icons/fa6";

const SelectMappingsValidate = () => {
  const navigate = useNavigate();
  const {
    mappings,
    setcurrentOntologyId,
    setontologyDataContext,
    setMappings,
    setJsonSchemaContext,
  } = useDataContext();
  const [mappingName, setMappingName] = useState<string>("");

  const location = useLocation();
  const mappingId = location.state?.mappingId;
  const ruleId = location.state?.ruleId;

  console.log(mappingId);
  console.log(ruleId);

  // const [selectedMappingId, setSelectedMappingId] = useState("");
  // const [selectedRuleId, setSelectedRuleId] = useState("");

  // const [dataQualityRules, setDataQualityRules] = useState<
  //   Array<{ id: string; name: string }>
  // >([]);

  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const getMappingData = async () => {
      if (mappingId) {
        setLoading(true);
        try {
          const response = await getMapping(mappingId);
          //console.log("Response de getMapping: ", response);
          if (response) {
            const { mapping_name, mapping, schema, ontology } = response.data;
            setMappings(mapping);
            setMappingName(mapping_name);
          }
        } catch (error) {
          console.error("error en getMappingData", error);
        }
        setLoading(false);
      }
    };
    getMappingData();
  }, [mappingId]);

  // const onClickMappingCard = (id: string) => {};

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="container">
          <h1 className="title-section">Data Quality</h1>

          <div className="data-quality-container">
            {mappings && (
              <div className="mappings-container">
                <h2 className="sub-title">Mappings</h2>
                <div className="mappings">
                  {Object.keys(mappings).map((key) => {
                    return (
                      <div className="mapping">
                        <ul className="list-container">
                          {mappings[key].map((element, index) => (
                            <li key={index} className="list-elem">
                              <div className="mapping-container">
                                <div className="value-wrapper">
                                  <div className="key-title">
                                    JSON schema value
                                  </div>
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
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  mappingCard: {
    display: "grid",
    gridTemplateColumns: "1fr 2fr",
    padding: "20px",
    backgroundColor: "#f0f0f0",
  },
};

export default SelectMappingsValidate;
