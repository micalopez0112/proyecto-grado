import React, { useState } from "react";
import Modal from "react-modal";
import { getAppliedMethods } from "../../services/mapsApi.ts";
import { Spinner } from "../Spinner/Spinner.tsx";
import "./DQModelCard.css";
import { FaEye } from "react-icons/fa";

const DQModelCard = ({
  id,
  name,
  style,
  onClickCallback = () => null,
}: {
  id: string;
  name: string;
  style?: React.CSSProperties;
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
              <h2>Applied to attributes:</h2>
              {modalData && modalData.length > 0 ? (
                <table className="table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {modalData.map((item: any, index) => (
                      <tr key={index}>
                        <td>{item.name}</td>
                        <td>{item.type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
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

      <div className="card" style={style} onClick={() => onClickCallback(id)}>
        <div>{name}</div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleOpenModal();
          }}
          className="info-button"
        >
          <FaEye size={20} />
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
