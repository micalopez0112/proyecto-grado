import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useDataContext } from "../../context/context.tsx";

interface ProtectedRouteProps {
  fallbackRoute: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ fallbackRoute }) => {
  const {externalFlow} = useDataContext();
  if (externalFlow) {
    return <Navigate to={fallbackRoute} replace />;
  }
  return <Outlet />;
};

export default ProtectedRoute;
