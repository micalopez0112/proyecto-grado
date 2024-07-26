import React, { useEffect } from 'react';
import "./OntologyData.css";
import { useDataContext } from '../context/context.tsx';

const OntologyData = () => {
  const currentOntoSelected = [];
  const isMapping = true;
  useEffect(() => {
  }, []);

  const { OntoElementSelected, setOntoElementSelected } = useDataContext();
  const handleClickOntoElem = (element) => {
    console.log(element);
    if (isMapping) {
      setOntoElementSelected(element);
    }
  };

  /*
  const handleClickOntoElem = (key: string, element: OntoElement) => {
    console.log(element);
    if (isMapping) {
      setOntoElementSelected(element);
      setMappings({
        ...mappings,
        [key]: [...(mappings[key] || []), element],
      });
    }
  };
  */

  const data = [
    {
      name: "Ontology 1",
      data: [
        {
          classes: [
            {
              name: "Class 1",
              iri: "http://example.com/class1",
            },
            {
              name: "Class 2",
              iri: "http://example.com/class2",
            },
          ],
          object_properties: [
            {
              name: "Object Property 1",
              iri: "http://example.com/objectproperty1",
            },
            {
              name: "Object Property 2",
              iri: "http://example.com/objectproperty2",
            },
          ],
          data_properties: [
            {
              name: "Data Property 1",
              iri: "http://example.com/dataproperty1",
            },
            {
              name: "Data Property 2",
              iri: "http://example.com/dataproperty2",
            },
          ],
        },
      ],
    },
    {
      name: "Ontology 2",
      data: [
        {
          classes: [
            {
              name: "Class 3",
              iri: "http://example.com/class3",
            },
            {
              name: "Class 4",
              iri: "http://example.com/class4",
            },
          ],
          object_properties: [
            {
              name: "Object Property 3",
              iri: "http://example.com/objectproperty3",
            },
            {
              name: "Object Property 4",
              iri: "http://example.com/objectproperty4",
            },
          ],
          data_properties: [
            {
              name: "Data Property 3",
              iri: "http://example.com/dataproperty3",
            },
            {
              name: "Data Property 4",
              iri: "http://example.com/dataproperty4",
            },
          ],
        },
      ],
    },
  ];

  return (
    <div className='onto-data-display-container'>
      <span className='text'>Your Ontologies Elements: </span>
      {OntoElementSelected != null ? <strong style={{ fontFamily: 'cursive' }}> An Element is selected {OntoElementSelected.iri}</strong> : null}
      {data?.map((ontology, i) => {
        return (
          <div className='onto-container' key={`ontology-${i}`}>
            <span className='ontology-title'>
              Ontology Elements: {ontology?.name}
            </span>
            {ontology?.data?.map((x, i) => (
              <div className='styled-input' key={`data-${i}`}>
                {x?.classes?.length > 0 && (
                  <>
                    <span className='text'>Classes:</span>
                    <div className='columns-container'>
                      {x?.classes?.map((c) => (
                        <div
                          className={`column-name-container ${isMapping ? 'is-mapping' : ''}`}
                          onClick={() => handleClickOntoElem(c)}
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
                          onClick={() => handleClickOntoElem(objectProperty)}
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
                          onClick={() => handleClickOntoElem(dataProperty)}
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
        );
      })}
    </div>
  );
};

export default OntologyData;
