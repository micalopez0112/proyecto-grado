import React, { useEffect } from 'react';
import "./OntologyData.css";
import { useDataContext} from '../context/context.tsx';
import { OntologyDataType } from '../types';



const OntologyData: React.FC<{}> = () => {
  const isMapping = true;

  const { OntoElementSelected, setOntoElementSelected, ontologyDataContext } = useDataContext();

  const handleClickOntoElem = (element: any, type:string) => {
    console.log("Onto element selected",element);
    if (isMapping) {
      setOntoElementSelected({type:type, ontoElement: element});
    }
  };

  useEffect(() => {
    console.log("Ontology Data Context: ", ontologyDataContext);
  }, []);



  return (
    <div className='onto-data-display-container'>
      <span className='ontology-title'>Elementos de la ontología: </span>
      {OntoElementSelected.type != undefined ? <strong style={{ fontFamily: 'cursive' }}> An Element is selected {OntoElementSelected.ontoElement.iri}</strong> : null}
      {ontologyDataContext?.ontoData.map((ontology, i) => (
        <div className='onto-container' key={`ontology-${i}`}>
          {ontology?.data?.map((x, i) => (
            <div className='styled-input' key={`data-${i}`}>
              {x?.classes?.length > 0 && (
                <>
                  <span className='text'>Classes:</span>
                  <div className='columns-container'>
                    {x?.classes?.map((c) => (
                      <div
                        className={`column-name-container ${isMapping ? 'is-mapping' : ''}`}
                        onClick={() => handleClickOntoElem(c,"class")}
                        key={c?.iri}
                      >
                        <span className='text'>{c?.name}</span>
                      </div>
                    ))}
                  </div>
                </>
              )}
              {x?.object_properties?.length > 0 && (
                <>
                  <span className='text'>Object Properties:</span>
                  <div className='columns-container'>
                    {x?.object_properties?.map((objectProperty) => (
                      <div
                        className={`column-name-container ${isMapping ? 'is-mapping' : ''}`}
                        onClick={() => handleClickOntoElem(objectProperty,"object_property")}
                        key={objectProperty?.iri}
                      >
                        <span className='text'>{objectProperty?.name}</span>
                      </div>
                    ))}
                  </div>
                </>
              )}
              {x?.data_properties?.length > 0 && (
                <>
                  <span className='text'>Data Properties:</span>
                  <div className='columns-container'>
                    {x?.data_properties?.map((dataProperty) => (
                      <div
                        className={`column-name-container ${isMapping ? 'is-mapping' : ''}`}
                        onClick={() => handleClickOntoElem(dataProperty,"data_property")}
                        key={dataProperty?.iri}
                      >
                        <span className='text'>{dataProperty?.name}</span>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default OntologyData;