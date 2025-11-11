"use client";

export function backendUrl() {

  if (typeof window === "undefined") {
    return "http://localhost:8080";
  } else {
    return `http://${window?.env?.MASTER_IP || "localhost"}`;
  }
}