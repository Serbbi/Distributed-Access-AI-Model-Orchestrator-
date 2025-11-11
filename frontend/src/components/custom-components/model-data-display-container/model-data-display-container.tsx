import { backendUrl } from "@/config";
import { useSearchContext } from "../search-provider";
import DataDisplay from "./components/display/data-display";
import { BaseItemDisplay } from "./components/display/display";
import ModelDisplay from "./components/display/model-display";
import { useEffect, useState } from "react";

export default function ModelDataDisplayContainer() {
  const [models, setModels] = useState([]);
  const [data, setData] = useState([]);

  async function fetchModels() {
    const response = await fetch(`${backendUrl()}/api/models`, {
      method: "GET",
      credentials: "include",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      console.log("Failed to fetch models");
    }

    const fetchedModels = await response.json();
    console.log(fetchedModels);
    setModels(fetchedModels);
  }

  async function fetchData() {
    const response = await fetch(`${backendUrl()}/api/data`, {
      method: "GET",
      credentials: "include",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      console.log("Failed to fetch data");
    }

    const fetchedData = await response.json();
    console.log(fetchedData);
    setData(fetchedData);
  }

  // Load data & models on first render
  useEffect(() => {
    fetchModels();
    fetchData();
  }, []);

  const fetchedContents: BaseItemDisplay[] = [...models, ...data];

  // const contents: BaseItemDisplay[] = [
  //   {
  //     title: "ICNN Predictor",
  //     type: "model",
  //     description: "A model that predicts the future",
  //     id: "1",
  //   },
  //   {
  //     title: "ICNN Data",
  //     type: "data",
  //     description: "Data for the ICNN model",
  //     id: "1",
  //   },
  // ];
  const { searchString } = useSearchContext();

  return (
    <div className="w-full h-full pt-20 px-4 flex-row flex gap-4">
      {fetchedContents
        .filter((content) => {
          return (
            content.title.toLowerCase().includes(searchString.toLowerCase()) ||
            content.type.toLowerCase().includes(searchString.toLowerCase())
          );
        })
        .map((content) =>
          content.type === "model" ? (
            <ModelDisplay
              key={content.title}
              title={content.title}
              id={content.id}
              description={content.description}
              data={data}
            />
          ) : (
            <DataDisplay
              key={content.title}
              title={content.title}
              id={content.id}
              description={content.description}
            />
          )
        )}
    </div>
  );
}
