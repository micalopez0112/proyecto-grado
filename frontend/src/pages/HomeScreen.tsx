import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchMappings } from '../services/mapsApi.ts';
import MappingCard from '../components/MappingCard.tsx';

const HomeScreen = () => {
  const navigate = useNavigate();
  const [mappings, setMappings] = useState<Array<{ id: string, name: string}>>([]);

  useEffect(() => {
    const retrieveMappings = async () => {
        const mappings = await fetchMappings();
        console.log("Mappings: ", mappings);
        //setMappings(mappings);
        if(mappings)
            setMappings(mappings.data);
    };
    retrieveMappings();
  }, []);

  const onClickMappingCard = (id: string) => {
    navigate('/Mappings', { state: { mappingId: id } });
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Pantalla de Inicio</h1>
      <button onClick={() => navigate('/OntologySelect')} style={styles.button}>Ir a Mappings</button>
      { mappings &&
      <div style={styles.dashboard}>
        {mappings.map(mapping => (
          <MappingCard
            key={mapping.id}
            id={mapping.id}
            name={mapping.name}
            style={styles.mappingCard}
            onClickCallback={onClickMappingCard}
          />
        ))}
      </div>
      }
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px',
    backgroundColor: '#f0f0f0',
    minHeight: '100vh',
  },
  title: {
    fontSize: '2em',
    color: '#000',
    marginBottom: '20px',
  },
  button: {
    padding: '10px 20px',
    fontSize: '1em',
    color: '#fff',
    backgroundColor: '#000',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    marginBottom: '20px',
  },
  dashboard: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '10px',
    width: '100%',
    maxWidth: '800px',
  },
  mappingCard: {
    backgroundColor: '#fff',
    padding: '15px',
    borderRadius: '5px',
    boxShadow: '0 2px 5px rgba(0, 0, 0, 0.1)',
    color: '#000',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease', 
  }
};

export default HomeScreen;
