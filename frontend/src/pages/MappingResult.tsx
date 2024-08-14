import React, {useState,useEffect} from 'react';
import Graph from 'react-graph-vis';
import { v4 as uuidv4 } from "uuid";
import { getMappingGraph } from '../services/mapsApi.ts';
import { useDataContext } from '../context/context.tsx';
import { useLocation } from 'react-router-dom';

//const OntologyData: React.FC<OntologyDataProps> = ({ ontoData }) => 


const MappingResult = () =>{
    const [graphData, setGraphData] = useState<any>(null);
    const {mappings} = useDataContext();
    const location = useLocation();
    const mapping_process = location.state?.mapping_process; //prop parameter via navigation

      const graph = graphData ?{
        nodes: graphData.nodes,
        edges: graphData.edges
        }: null

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
      }

      useEffect(() => {
        const getGraphData = async () => {
            try{
                if(mapping_process!== ''){
                    const response = await getMappingGraph(mapping_process);
                    console.log("Mapping Graph: ", response);
                    if(response)
                        setGraphData(response.data);
                }
            }
            catch(error){
                console.error("Error en getGraphData (MappingResult)", error);
            }
        };
        getGraphData();

      },[]);

    return(
        <div className='App'>
            <h1>Resultado del mapeo</h1>
            <div className='content-container'>
                <div className='content-box'>
                    <div style={{}}>
                      <h3>Entidades de la ontología y mapeos involucrados</h3>
                    </div>
                    <div style={
                        {display:'grid',
                        backgroundColor:'white',
                        height:'100%',
                        width:'100%',
                        borderRadius: '8px',
                        gridTemplateColumns: '1fr 3fr',
                      }
                        }>
                        <div style={
                          { display:'flex',
                            flexDirection:'column',
                            backgroundColor:'#e5efff',
                            height:'100%',
                            padding:'5px',
                            borderRadius: '8px',
                          }
                          
                          }>
                            <h4>Correspondencias JSON Schema - Ontologia</h4>
                            <div> {/*table div ?? */}
                              {
                                 Object.keys(mappings).map((key) => {
                                  return (
                                      <div> {/*Row div ?? */}
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
                            </div>
                        </div>
                        <div>
                          {graphData ?
                          <Graph
                              key={uuidv4()}
                              graph={graph}
                              options={options}
                              events={{}}
                          /> : null}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

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