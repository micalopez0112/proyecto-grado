import React, { useEffect, useState } from "react";
import "./OntologyData.css";
import { useDataContext } from "../context/context.tsx";
import { OntologyDataType } from "../types";
import Modal from "react-modal";
import { OntoElement } from "../context/context.tsx";
import { IoRemoveOutline } from "react-icons/io5";

Modal.setAppElement("#root");

const OntologyData: React.FC<{}> = () => {
  const isMapping = true;

  const { OntoElementSelected, setOntoElementSelected, ontologyDataContext } =
    useDataContext();
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [rangeList, setRangeList] = useState<Array<OntoElement>>([]);
  const [selectedRange, setSelectedRange] = useState<Array<OntoElement>>([]);
  const [objectPropertyElement, setObjectPropertyElement] = useState<any>();

  const handleClickOntoElem = (element: any, type: string) => {
    if (isMapping && type !== "object_property") {
      setOntoElementSelected({ type: type, ontoElement: element });
    } else if (isMapping && type === "object_property") {
      setRangeList([...rangeList, element.range]);
      setObjectPropertyElement(element);
      setModalIsOpen(true);
      //agregar boton de aceptar y ahí hacer el setOntoElementSelected para este caso.
    }
  };

  const handleAddElemToRange = (rangeItem: OntoElement) => {
    if (rangeItem === undefined) return;
    else {
      if (selectedRange.includes(rangeItem)) {
        setSelectedRange(
          selectedRange.filter((selected) => selected !== rangeItem)
        );
      } else {
        setSelectedRange([...selectedRange, rangeItem]);
      }
    }
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setRangeList([]);
    setObjectPropertyElement({});
    setSelectedRange([]);
  };

  const confirmationModal = (objectPropertyElement: any) => {
    //use
    setOntoElementSelected({
      type: "object_property",
      ontoElement: {
        name: objectPropertyElement.name,
        iri: objectPropertyElement.iri,
        range: selectedRange,
      },
    });

    setSelectedRange([]);
    setObjectPropertyElement({});
    setRangeList([]);
    setModalIsOpen(false);
  };

  useEffect(() => {}, []);

  return (
    <div className="container">
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={() => setModalIsOpen(false)}
        shouldCloseOnOverlayClick={false}
        style={ModalStyles}
      >
        <div style={ModalStyles.modalContent}>
          <label style={{ border: "solid 3px black", padding: "2px" }}>
            Mapeo de rango
          </label>
          <div style={{ marginTop: "10px" }}>
            <p>Selecciona los elementos del rango que deben ser mapeados:</p>
            <ul style={ModalStyles.listStyle}>
              {rangeList.map((item, i) => (
                <li
                  key={i}
                  onClick={() => handleAddElemToRange(item)}
                  style={{
                    ...ModalStyles.listItemStyle,
                    ...(selectedRange.includes(item)
                      ? ModalStyles.selectedItemStyle
                      : {}),
                  }}
                >
                  {item.name}
                </li>
              ))}
            </ul>
          </div>
          <div style={ModalStyles.modalfooter}>
            <button
              className="button"
              style={ModalStyles.modalCancelButton}
              onClick={() => closeModal()}
            >
              Cerrar
            </button>
            <button
              style={ModalStyles.modalOkButton}
              onClick={() => confirmationModal(objectPropertyElement)}
            >
              Aceptar
            </button>
          </div>
        </div>
      </Modal>

      <div className="title-wrapper">
        <h1 className="title">Elementos de la ontología</h1>
      </div>
      {OntoElementSelected.type != undefined ? (
        <strong style={{ fontFamily: "cursive" }}>
          An Element is selected {OntoElementSelected.ontoElement.iri}
        </strong>
      ) : null}
      {ontologyDataContext?.ontoData.map((ontology, i) => (
        <div className="onto-container" key={`ontology-${i}`}>
          {ontology?.data?.map((x, i) => (
            <div className="styled-input" key={`data-${i}`}>
              {x?.classes?.length > 0 && (
                <>
                  <div className="ontolo-elems-container">
                    <div className="onto-elem">Classes:</div>
                    <div className="columns-container">
                      {x?.classes?.map((c) => (
                        <div
                          className={`column-name-container ${
                            isMapping ? "is-mapping" : ""
                          }`}
                          onClick={() => handleClickOntoElem(c, "class")}
                          key={c?.iri}
                        >
                          <div className="line">
                            <IoRemoveOutline size={20} />
                          </div>
                          <span className="text">{c?.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
              {x?.object_properties?.length > 0 && (
                <>
                  <div className="ontolo-elems-container">
                    <div className="onto-elem">Object Properties:</div>
                    <div className="columns-container">
                      {x?.object_properties?.map((objectProperty, index) => (
                        <div
                          className={`column-name-container ${
                            isMapping ? "is-mapping" : ""
                          }`}
                          onClick={() =>
                            handleClickOntoElem(
                              objectProperty,
                              "object_property"
                            )
                          }
                          key={`${objectProperty?.iri}-${index}`}
                        >
                          <div className="line">
                            <IoRemoveOutline size={20} />
                          </div>
                          <span className="text">{objectProperty?.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
              {x?.data_properties?.length > 0 && (
                <>
                  <div className="ontolo-elems-container">
                    <div className="onto-elem">Data Properties:</div>
                    <div className="columns-container">
                      {x?.data_properties?.map((dataProperty) => (
                        <div
                          className={`column-name-container ${
                            isMapping ? "is-mapping" : ""
                          }`}
                          onClick={() =>
                            handleClickOntoElem(dataProperty, "data_property")
                          }
                          key={dataProperty?.iri}
                        >
                          <div className="line">
                            <IoRemoveOutline size={20} />
                          </div>
                          <span className="text">{dataProperty?.name}</span>
                        </div>
                      ))}
                    </div>
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

const ModalStyles: { [key: string]: React.CSSProperties } = {
  content: {
    top: "50%",
    left: "50%",
    right: "auto",
    bottom: "auto",
    marginRight: "-50%",
    transform: "translate(-50%, -50%)",
  },
  modalContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    width: "220px",
    backgroundColor: "white",
    padding: "20px",
    borderRadius: "8px",
    boxShadow: "4px 4px 6px rgba(0, 0, 0, 0.1)",
  },
  listStyle: {
    listStyleType: "none",
    padding: 0,
  },
  listItemStyle: {
    padding: "10px",
    backgroundColor: "#f0f0f0",
    margin: "5px 0",
    cursor: "pointer",
  },
  selectedItemStyle: {
    backgroundColor: "#007BFF",
    color: "white",
    fontWeight: "bold",
  },
  modalfooter: {
    marginTop: "20px",
    display: "flex",
    justifyContent: "flex-end",
    width: "100%",
  },
  modalcontainer: {},
  modalCancelButton: {
    backgroundColor: "#ff3f1b",
    color: "white",
    padding: "10px",
    borderRadius: "5px",
    marginRight: "8px",
    cursor: "pointer",
  },
  modalOkButton: {
    backgroundColor: "#ffffff",
    color: "black",
    padding: "10px",
    borderRadius: "5px",
    cursor: "pointer",
  },
};

export default OntologyData;
