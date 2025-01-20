import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useDataContext } from "../../context/context.tsx";
import {toast} from "react-toastify";
import { fetchMappings,connectNeo4jDB,getDatasetMappings} from "../../services/mapsApi.ts";
import MappingCard from "../../components/MappingCard.tsx";
import { Spinner } from "../../components/Spinner/Spinner.tsx";
import "./MappingsScreen.css";

const MappingsScreen = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // parameters from query string
  const connectionString = searchParams.get("connection_string");
  const collectionPathParam = searchParams.get("collection_path");
  const idDataset = searchParams.get("id_dataset");

  const [mappings, setMappings] = useState<Array<{ id: string; name: string }>>(
    []
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const {externalFlow,setExternalFlow,externalDatasetId,setExternalDatasetId,collectionPath,setCollectionPath} =
  useDataContext();


  useEffect(() => {
    console.log("Se ejecuta useEffect con dependencia");
    const checkFlow = async () => {
      console.log("Search params size: ", searchParams.size);
    if(searchParams.size > 0){
      if(connectionString && collectionPathParam && idDataset){
        //erase navigation stack
        console.log("FLUJO EXTERNO")
        console.log("Connection string: ", connectionString);
        console.log("Collection path: ", collectionPathParam);
        console.log("Id dataset: ", idDataset);

        //Check if parameters are not null
        //if are null, throw error and return

        const decodedConnectionString = connectionString
        ? decodeURIComponent(connectionString)
        : "";

        console.log("#DECODED connection_string#: ", decodedConnectionString);

        setExternalFlow(true);
        setExternalDatasetId(idDataset);
        setCollectionPath(collectionPathParam);

    
        //call update neo4j connection
        //set info in context for external app flow
        const credentials = decodedConnectionString.split("$");
        const uri = credentials[0];
        const user = credentials[1];
        const password = credentials[2];
        
        setLoading(true);
        const responseUpdateNeo4j = await connectNeo4jDB(uri,user,password);
        if(responseUpdateNeo4j?.status === 200){
          setLoading(false);
          //capaz cambiar a que si recien acá da 200 OK guardar en contexto
          toast.success("The external connection has been established");
          console.log("Response update neo4j en MappingsScreen.tsx: ",responseUpdateNeo4j);
          if(idDataset){
            await retrieveMappings(idDataset);
          }
        }
      }
    }
    else{
      console.log("FLUJO INTERNO")
      await retrieveMappings("");
    }
    };
    checkFlow();
  },[searchParams]);

  // useEffect(() => {
  //   console.log("Se ejecuta useEffect");
  //   console.log("External flow: ", externalFlow);
  //   console.log("External dataset id: ", externalDatasetId);
    
  //   retrieveMappings();
  // }, [externalFlow, externalDatasetId]);

  const retrieveMappings = async (datasetId:string) => {
    setLoading(true);
    console.log("Mappings antes de fetchMappings: ", mappings);
    if(datasetId !== ""){
      const datasetMappings = await getDatasetMappings(datasetId);
      console.log("Dataset mappings from idDataset: ", datasetMappings);
      if (datasetMappings && idDataset){
        console.log("Mapping data from dataset id: ", datasetMappings.data);
        //Es necesario el map porque viene con distintos campos
        const transformedMappings = datasetMappings.data.map((item: any) => ({
          id: item.idMapping,  
          name: item.name,     
        }));
        setMappings(transformedMappings);
      }
    }
    else{
      const datasetMappings = await fetchMappings();
      if (datasetMappings && !externalDatasetId){
        console.log("Mapping data from dataset id: ", datasetMappings.data);
        setMappings(datasetMappings.data);
      } 
        
    }
    console.log("Mappings: ", mappings);
    setLoading(false);
    // }
  };

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

  const newMapping = () =>{
    if(externalFlow){
      //hay que navegar a OntologySelect pero:
      //1. setear el id del dataset
      //2. setear la collection path
      console.log("#Antes de navegar a OntologySelect en externalFlow#");
      console.log("External dataset id: ", externalDatasetId);
      console.log("Collection path: ", collectionPath);
      navigate("/OntologySelect");
    }
    else{
      navigate("/OntologySelect");
    }
    
  }

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
              onClick={() => newMapping()}
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
