import React from "react";
import "./App.css";
import Json from "./components/JsonSchema.tsx";
import OntologyData from "./components/OntologyData.tsx";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useNavigate,
  Outlet,
} from "react-router-dom";
import HomeScreen from "./pages/home/HomeScreen.tsx";
import DataQualityScreen from "./pages/data-quality/DataQualityScreen.tsx";
import OntologySelectScreen from "./pages/mappings/OntologySelect.tsx";
import MappingsScreen from "./pages/mappings/MappingsScreen.tsx";
import MappingResult from "./pages/MappingResult.tsx";
import { Mapping } from "./pages/mappings/Mapping.tsx";
import SchemaSelect from "./pages/mappings/SchemaSelect.tsx";
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomeScreen />} />
        <Route path="/MappingsScreen" element={<MappingsScreen />} />
        <Route path="/DataQualityScreen" element={<DataQualityScreen />} />
        <Route path="/OntologySelect" element={<OntologySelectScreen />} />
        <Route path="/SchemaSelect" element={<SchemaSelect />} />
        <Route path="/Mapping" element={<Mapping />} />
        <Route path="/Ontology" element={<OntologyData />} />
        <Route path="/Result" element={<MappingResult />} />
      </Routes>
    </Router>
  );
}

export default App;
