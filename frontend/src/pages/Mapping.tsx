import React from 'react'
import Json from '../components/JsonSchema.tsx'
import OntologyData from '../components/OntologyData.tsx';
import { useNavigate } from "react-router-dom";
import { useDataContext } from '../context/context.tsx';

export const Mapping = () => {

    const navigate = useNavigate();

    const handleClick = () => {
        navigate('./Ontology');
    }

    const { mappings,addNewMapping,clearMappings } = useDataContext();


    return(
    <div className="App">
        <div className='content-container'>
            <div className='content-box'>
                <Json></Json>    
            </div>
            <div className='content-box'>
                <OntologyData></OntologyData>
            </div>  
        </div>
        <div>
            <h1>Mappings</h1>
            <button onClick={addNewMapping}>Agregar mapping</button>
            <button onClick={clearMappings}>Limpiar mappings</button>
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
        </div>
    </div>
    )
}