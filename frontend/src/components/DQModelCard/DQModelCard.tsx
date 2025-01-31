import React, { useState } from "react";
import Modal from "react-modal";
import { getAppliedMethods } from "../../services/mapsApi.ts";
import { Spinner } from "../Spinner/Spinner.tsx";
import { FaMagnifyingGlass } from "react-icons/fa6";
import "./DQModelCard.css";

const DQModelCard = ({
  id,
  name,
  style,
  onClickCallback = () => null,
}: {
  id: string;
  name: string;
  style: React.CSSProperties;
  onClickCallback?: (id: string) => void;
}) => {
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [modalData, setModalData] = useState([]);

  const closeModal = () => setModalIsOpen(false);

  const handleOpenModal = async () => {
    if (id) {
      setLoading(true);
      setModalIsOpen(true);
      try {
        const response = await getAppliedMethods(id);
        setModalData(response);
      } catch (error) {
        console.error("Error fetching mapping details:", error);
        setModalData([]);
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
          {loading ? (
            <Spinner />
          ) : (
            <div>
              <h2>Details</h2>
              {modalData && modalData.length > 0 ? (
                <ul>
                  {modalData.map((item: any, index: number) => (
                    <li key={index}>
                      <strong>{item.name}:</strong> {item.type}
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No data available.</p>
              )}
            </div>
          )}
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
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleOpenModal();
          }}
          className="info-button"
        >
          <FaMagnifyingGlass size={20} />
        </button>
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

export default DQModelCard;
