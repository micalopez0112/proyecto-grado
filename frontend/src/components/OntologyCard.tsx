import React from "react";

const OntologyCard = ({
  id,
  name,
  style,
  onClickCallback,
}: {
  id: string;
  name: string;
  style: any;
  onClickCallback: (id: string) => void;
}) => {
  return (
    <div style={style} onClick={() => onClickCallback(id)}>
      <h3>Ontology: </h3>
      <p>{name}</p>
      <p>
        <strong>Ontology ID:</strong> {id}
      </p>
    </div>
  );
};

export default OntologyCard;
