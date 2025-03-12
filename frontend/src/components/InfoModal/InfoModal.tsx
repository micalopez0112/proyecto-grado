import React, { useState } from "react";
import Modal from "react-modal";
import { IoIosInformationCircleOutline } from "react-icons/io";
import "./InfoModal.css";

const InfoModal = ({ text }) => {
  const [modalIsOpen, setModalIsOpen] = useState(false);

  const openModal = () => {
    console.log("Opening modal", modalIsOpen); // Debugging
    setModalIsOpen(true);
  };

  const closeModal = () => setModalIsOpen(false);

  return (
    <div className="info">
      <IoIosInformationCircleOutline
        size={30}
        className="info-icon"
        onClick={openModal}
      />

      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        shouldCloseOnOverlayClick={true}
        style={ModalOntoStyles}
      >
        <div className="modal-content">
          <p>{text}</p>
          <button className="button" onClick={closeModal}>
            Close
          </button>
        </div>
      </Modal>
    </div>
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
    width: "1000px",
    display: "flex",
    justifyContent: "center",
  },
  modalContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
  },
};

export default InfoModal;
