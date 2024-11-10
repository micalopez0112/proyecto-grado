import React,{useState, useEffect} from 'react'
import { useDataContext } from '../../../context/context.tsx';
import { useNavigate } from "react-router-dom";
import { Spinner } from '../../../components/Spinner/Spinner.tsx';
import { fetchDatasets } from '../../../services/mapsApi.ts';
import MappingCard from '../../../components/MappingCard.tsx';

import "./DatasetsScreen.css";

const DatasetsScreen = () => {

    
    const [loading, setLoading] = useState<boolean>(false);
    const [datasets, setDatasets] = useState<Array<{ id: string; collection_name: string; properties}>>([]);
    const navigate = useNavigate();
    
    useEffect(() => {
        const retrieveDatasets = async () => {
            try{
                setLoading(true);
                const response = await fetchDatasets();
                if(response?.status === 200){
                    const datasets = response.data;
                    setDatasets(datasets);
                    console.log("Datasets: ", datasets);
                }
                setLoading(false);
            }
            catch(error){
                console.log("Error while loading datasets");
            }
        }
        retrieveDatasets();
    },[]);
    
    const selectDataset = (id:string) =>{
        navigate(`/DataQualityScreen/${id}`);
    }

    return (
        <>
        {loading ? (<Spinner />) 
        :
         (<>
         <div className='container'>
            <h1 className="title-section">Available Datasets</h1>
            <p className="subtitle">Select a dataset to evaluate its attributes quality</p>
            <div className='dataset-container'>
                <div className='dataset-list-container'>
                    {datasets.map((dataset) => (
                        <MappingCard
                            key={dataset.id}
                            id={dataset.id}
                            name={dataset.collection_name}
                            onClickCallback={() => selectDataset(dataset.id)}
                            style= {styles.datasetMappingCard}
                            />
                    ))}
                </div>
            </div>
         </div>
         </>)
        }
        </>
    );
}

const styles: { [key: string]: React.CSSProperties } = {
    datasetMappingCard: {
      display: "flex",
      padding: 10,
      cursor: "pointer",
      borderRadius: 5,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "#fff",
    },
  };

export default DatasetsScreen;