import React from "react";

const MappingCard = ({
  id,
  name,
  style,
  onClickCallback = () => null,
}: {
  id: string;
  name: string;
  style: any;
  onClickCallback?: (id: string) => void;
}) => {
  return (
    <div style={style} onClick={() => onClickCallback(id)}>
      <div>{name}</div>
      <div>
        <strong>Mapping ID:</strong> {id}
      </div>
    </div>
  );
};

export default MappingCard;
