import React from 'react'
import Json from '../components/JsonSchema.tsx'
import OntologyData from '../components/OntologyData.tsx';
import { useNavigate } from "react-router-dom";

export const Mapping = () => {

    const navigate = useNavigate();

    const handleClick = () => {
        navigate('./Ontology');
    }
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
    </div>
    )
}