"use client";

import ModelDataDisplayContainer from "@/components/custom-components/model-data-display-container/model-data-display-container";

export default function HomePage() {
  return (
      <div
        style={{
          width: "80%",
          height: "100vh",
          display: "flex",
          justifyContent: "start",
          alignItems: "center",
        }}
      >
        <ModelDataDisplayContainer />
      </div>
  );
}
