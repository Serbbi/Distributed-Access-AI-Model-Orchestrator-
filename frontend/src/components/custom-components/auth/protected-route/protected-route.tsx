"use client";

// import { useAuth } from "../auth-provider/auth-provider";

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {

  // TEMPORARY: Remove comment lines BEFORE pushing!!!!!

  // const { hasValidSession } = useAuth();

  // if (!hasValidSession) {
  //   return null;
  // }

  return children;
}
