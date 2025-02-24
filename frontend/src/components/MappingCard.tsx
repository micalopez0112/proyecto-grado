import React, { useState } from "react";
import Modal from "react-modal";
import { deleteMapping, getMapping } from "../services/mapsApi.ts";
import { useDataContext } from "../context/context.tsx";
import MappingList from "./MappingList.tsx";
import { Spinner } from "./Spinner/Spinner.tsx";
import { FaTrash } from "react-icons/fa6";
import { FaEye } from "react-icons/fa";
import "./MappingCard.css";

const MappingCard = ({
  id,
  name,
  style,
  onClickCallback = () => null,
  onDeleteCallback = () => null,
  includeMappingInfo = false,
  includeTrash = false,
}: {
  id: string;
  name: string;
  style: React.CSSProperties;
  onClickCallback?: (id: string) => void;
  onDeleteCallback?: (id: string) => void;
  includeMappingInfo?: boolean;
  includeTrash?: boolean;
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

  const handleOpenModal = async () => {
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

  const handleDeleteMapping = async () => {
    if (!id) return;

    const userConfirmed = window.confirm(
      `Are you sure you want to delete the mapping "${name}"? This action cannot be undone.`
    );
    if (!userConfirmed) return;

    try {
      const response = await deleteMapping(id);

      if (response && response.status === 200) {
        onDeleteCallback(id);
        alert(`Mapping "${name}" deleted successfully.`);
      } else {
        alert(`Failed to delete mapping "${name}".`);
      }
    } catch (error) {
      alert(`Error deleting mapping: ${error.message || "Unknown error"}`);
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
      <div
        className="mapping-card"
        style={style}
        onClick={() => onClickCallback(id)}
      >
        <div>{name}</div>

        {includeMappingInfo && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleOpenModal();
            }}
            className="info-button"
          >
            <FaEye size={24} />
          </button>
        )}
        {includeTrash && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDeleteMapping();
            }}
            className="trash-icon"
            disabled={loading}
          >
            {loading ? "Deleting..." : <FaTrash />}
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
