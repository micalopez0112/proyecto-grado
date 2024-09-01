import React, { useState, useEffect } from "react";
import Graph from "react-graph-vis";
import { v4 as uuidv4 } from "uuid";
import { getMappingGraph } from "../services/mapsApi.ts";
import { useDataContext } from "../context/context.tsx";
import { useLocation } from "react-router-dom";

import "./MappingResult.css";
import MappingList from "../components/MappingList.tsx";

//const OntologyData: React.FC<OntologyDataProps> = ({ ontoData }) =>

const MappingResult = () => {
  const [graphData, setGraphData] = useState<any>(null);
  const { mappings } = useDataContext();
  const location = useLocation();
  const mapping_process = location.state?.mapping_process; //prop parameter via navigation

  const graph = graphData
    ? {
        nodes: graphData.nodes,
        edges: graphData.edges,
      }
    : null;

  const options = {
    edges: {
      color: "#000000",
      arrows: {
        to: false,
      },
      font: {
        face: "RobotoBold",
      },
      length: 250,
    },
    nodes: {
      shape: "box",
      color: "rgb(51, 102, 204)",
      margin: 6,
      font: {
        color: "white",
        face: "Roboto",
      },
    },
  };

  useEffect(() => {
    const getGraphData = async () => {
      try {
        if (mapping_process !== "") {
          const response = await getMappingGraph(mapping_process);
          console.log("Mapping Graph: ", response);
          if (response) setGraphData(response.data);
        }
      } catch (error) {
        console.error("Error en getGraphData (MappingResult)", error);
      }
    };
    getGraphData();
  }, []);

  return (
    <div className="App">
      <h1>Resultado del mapeo</h1>
      <div className="result-container">
        <div className="result-box">
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              backgroundColor: "#0d245b",
              height: "100%",
              padding: "0px 5px",
              borderRadius: "8px",
            }}
          >
            <h4 className="title">Correspondencias JSON Schema - Ontologia</h4>
            <div className="result-mapping-wrapper">
              <MappingList isResult={true} />
            </div>
          </div>
          <div>
            {graphData ? (
              <Graph
                key={uuidv4()}
                graph={graph}
                options={options}
                events={{}}
              />
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MappingResult;
/*
{
                Object.keys(mappings).map((key) => {
                    return (
                        <div>
                            <h2>{key}</h2>
                            <ul>
                                {
                                    mappings[key].map((element) => {
                                        return <li>{element.name}</li>
                                    })
                                }
                            </ul>
                        </div>
                    )
                })
            }

*/
