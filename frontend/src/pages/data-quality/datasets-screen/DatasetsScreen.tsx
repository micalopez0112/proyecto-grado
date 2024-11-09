import React,{useState, useEffect} from 'react'
import { useDataContext } from '../../../context/context.tsx';
import { useNavigate } from "react-router-dom";
import { Spinner } from '../../../components/Spinner/Spinner.tsx';
import { fetchDatasets } from '../../../services/mapsApi.ts';

import "./DatasetsScreen.css";

const DatasetsScreen = () => {

    
    const [loading, setLoading] = useState<boolean>(false);
    const [datasets, setDatasets] = useState<Array<{ id: string; name: string; properties}>>([]);

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
    

    return (
        <>
        {loading ? (<Spinner />) 
        :
         (<>
         <div className='container'>
            <h1 className="title-section">Available Datasets</h1>
            <div className='dataset-container'>
                <div className='dataset-list-container'>
                    {datasets.map((dataset) => (
                        <div className='dataset-card'>
                            {/* <h2 className='sub-title'>{dataset.name}</h2>
                            <p>{dataset.properties}</p> */}
                        </div>
                    ))}
                    <div className='dataset-card'>
                            <h2 className='sub-title'>name</h2>
                            <p>properties</p>
                        </div>
                </div>
            </div>
         </div>
         </>)
        }
        </>
    );
}

export default DatasetsScreen;