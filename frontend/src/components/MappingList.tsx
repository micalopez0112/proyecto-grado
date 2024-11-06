import React from "react";
import { FaTrash } from "react-icons/fa";
import { FaArrowRightLong } from "react-icons/fa6";
import { useDataContext } from "../context/context.tsx";
import "./MappingList.css";

const MappingList = ({ isResult }) => {
  const { mappings, removeMapping } = useDataContext();

  console.log("mappings", { mappings });
  return (
    <div className="mappings">
      {Object.keys(mappings).map((key) => {
        return (
          <div className="mapping">
            <ul className="list-container">
              {mappings[key].map((element, index) => (
                <li key={index} className="list-elem">
                  <div className="mapping-elem">
                    <div className="value-wrapper">
                      <div className="key-title">JSON schema value</div>
                      <div className="key-text" title={key}>
                        {key}
                      </div>
                    </div>

                    <FaArrowRightLong className="arrow-icon" />
                    <div className="value-wrapper">
                      <div className="element-title">Ontology element</div>
                      <div className="element-name" title={element.name}>
                        {element.name}
                      </div>
                    </div>
                  </div>

                  {!isResult && (
                    <button
                      className="trash-icon"
                      style={{ marginLeft: "5px" }}
                      onClick={() =>
                        removeMapping(
                          key,
                          element as { name: string; iri: string }
                        )
                      }
                    >
                      <FaTrash />
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </div>
  );
};

export default MappingList;
