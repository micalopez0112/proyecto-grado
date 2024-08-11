import React, {useState,useEffect} from 'react';
import Graph from 'react-graph-vis';
import { v4 as uuidv4 } from "uuid";
import { getMappingGraph } from '../services/mapsApi.ts';
import { useDataContext } from '../context/context.tsx';

const MappingResult = () =>{
    const [graphData, setGraphData] = useState<any>(null);
    const {currentMappingProcessId} = useDataContext();

  /*  const graph = {
        nodes: [
          { id: 1, label: "Node 1", title: "node 1 tootip text" },
          { id: 2, label: "Node 2", title: "node 2 tootip text" },
          { id: 3, label: "Node 3", title: "node 3 tootip text" },
          { id: 4, label: "Node 4", title: "node 4 tootip text" },
          { id: 5, label: "Node 5", title: "node 5 tootip text" }
        ],
        edges: [
          { from: 1, to: 2 },
          { from: 1, to: 3 },
          { from: 2, to: 4 },
          { from: 2, to: 5 }
        ]
      };*/
    
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
                if(currentMappingProcessId){
                    const response = await getMappingGraph(currentMappingProcessId);
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
                    <h3>Entidades de la ontología y mapeos involucrados</h3>
                    <div style={
                        {display:'grid',
                        backgroundColor:'#efddff',
                        height:'100%',
                        width:'100%',
                        borderRadius: '8px',}
                        }>
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
    );
}

export default MappingResult;