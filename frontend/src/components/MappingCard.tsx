import React, { useState } from "react";
import Modal from "react-modal";
import { getMapping } from "../services/mapsApi.ts";
import { useDataContext } from "../context/context.tsx";
import MappingList from "./MappingList.tsx";
import { Spinner } from "./Spinner/Spinner.tsx";
import { FaMagnifyingGlass } from "react-icons/fa6";
import "./MappingCard.css";

const MappingCard = ({
  id,
  name,
  style,
  onClickCallback = () => null,
  includeMappingInfo = false,
}: {
  id: string;
  name: string;
  style: React.CSSProperties;
  onClickCallback?: (id: string) => void;
  includeMappingInfo?: boolean;
  mappingDetails?: {
    mapping_name: string;
    mapping: string;
    schema: string;
    ontology: string;
  } | null;
}) => {
  const { setMappings } = useDataContext();
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [loading, setLoading] = useState<boolean>(false);

  const closeModal = () => setModalIsOpen(false);

  const handeOpenModal = async () => {
    if (id) {
      setLoading(true);
      setModalIsOpen(true);
      try {
        const response = await getMapping(id);
        console.log({ response });
        const { mapping } = response?.data;
        setMappings(mapping);
      } catch (error) {
        console.error("Error fetching mapping details:", error);
      }
      setLoading(false);
    }
  };

  return (
    <>
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        shouldCloseOnOverlayClick={false}
        style={ModalOntoStyles}
      >
        <div style={ModalOntoStyles.modalContent}>
          {loading ? <Spinner /> : <MappingList isResult={true} />}
          <button className="button" onClick={closeModal}>
            Close
          </button>
        </div>
      </Modal>
      <div style={style} onClick={() => onClickCallback(id)}>
        <div>{name}</div>

        {includeMappingInfo && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              handeOpenModal();
            }}
            className="info-button"
          >
            <FaMagnifyingGlass size={20} />{" "}
          </button>
        )}
      </div>
    </>
  );
};

const ModalOntoStyles: { [key: string]: React.CSSProperties } = {
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
    width: "1000px",
    height: "500px",
  },
};

export default MappingCard;
