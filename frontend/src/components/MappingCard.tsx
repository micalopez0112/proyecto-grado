import React from 'react';


const MappingCard = ({ id, name, style , onClickCallback }: { id: string, name: string,style:any, onClickCallback: (id: string) => void }) => {
    return (
        <div style={style} onClick={() => onClickCallback(id)}>
            <h3>{name}</h3>
            <p><strong>Mapping ID:</strong> {id}</p>
        </div>
    );
};

export default MappingCard;