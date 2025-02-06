import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useDataContext } from "../../context/context.tsx";

interface ProtectedRouteProps {
  fallbackRoute: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ fallbackRoute }) => {
  const {externalFlow} = useDataContext();

  console.log("EXTERNAL FLOW in ProtectedRoute: ", externalFlow);
  if (externalFlow) {
    return <Navigate to={fallbackRoute} replace />;
  }
  return <Outlet />;
};

export default ProtectedRoute;
