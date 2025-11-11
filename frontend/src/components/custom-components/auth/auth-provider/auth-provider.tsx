"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { backendUrl } from "@/config";
import React from "react";

interface Props {
  children: React.ReactNode | React.ReactNode[];
}

interface AuthContextInterface {
  hasValidSession: boolean;
  checkSessionToken?: () => void;
}

const AuthContext = createContext<AuthContextInterface>({
  hasValidSession: false,
});

export function AuthProvider({ children }: Props) {
  const [hasValidSession, setHasValidSessions] = useState<boolean>(false);
  const path = usePathname();
  const router = useRouter();

  const checkSessionToken = useCallback(async () => {
    try {
      const response = await fetch(`${backendUrl()}/sessions/whoami`, {
        credentials: "include",
        headers: { Accept: "application/json" },
      });

      if (response.ok) {
        setHasValidSessions(true);
      } else {
        router.push("/login"); 
      }
    } catch (error) {
      console.error("Error checking session:", error);
      setHasValidSessions(false);
      router.push("/login"); 
    } 
  }, [router]);

  useEffect(() => {
    checkSessionToken();
  }, [checkSessionToken, path])


  return (
    <AuthContext.Provider value={{ hasValidSession, checkSessionToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
