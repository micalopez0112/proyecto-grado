import React from "react";
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomeScreen from "./pages/home/HomeScreen.tsx";
import DataQualityScreen from "./pages/data-quality/data-quality-screen/DataQualityScreen.tsx";
import OntologySelectScreen from "./pages/mappings/OntologySelect.tsx";
import MappingsScreen from "./pages/mappings/MappingsScreen.tsx";
import MappingResult from "./pages/MappingResult.tsx";
import { Mapping } from "./pages/mappings/Mapping.tsx";
import SchemaSelect from "./pages/mappings/SchemaSelect.tsx";
import SelectMappingsValidate from "./pages/data-quality/select-mappings-validate/SelectMappingsValidate.tsx";
import OntologyData from "./components/OntologyData.tsx";
import Navbar from "./components/Navbar/Navbar.tsx";

function App() {
  return (
    <Router>
      <Navbar /> {/* Add the Navbar here */}
      <Routes>
        <Route path="/" element={<HomeScreen />} />
        <Route path="/MappingsScreen" element={<MappingsScreen />} />
        <Route path="/DataQualityScreen" element={<DataQualityScreen />} />
        <Route path="/OntologySelect" element={<OntologySelectScreen />} />
        <Route path="/SchemaSelect" element={<SchemaSelect />} />
        <Route path="/Mapping" element={<Mapping />} />
        <Route path="/Ontology" element={<OntologyData />} />
        <Route path="/Result" element={<MappingResult />} />
        <Route
          path="/SelectMappingsValidate"
          element={<SelectMappingsValidate />}
        />
      </Routes>
    </Router>
  );
}

export default App;
