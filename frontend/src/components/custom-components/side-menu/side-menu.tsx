"use client";

import { Button } from "@/components/ui/button";
import { backendUrl } from "@/config";
import { MountainSnow } from "lucide-react";
import { JobList } from "./components/job-list";

export default function SideBar() {
  // function getModels() {
  //   fetch(`${backendUrl()}/models`, {
  //     credentials: "include",
  //     headers: { Accept: "application/json" },
  //   })
  //     .then((response) => response.text())
  //     .then((data) => console.log(data));
  // }

  function hello() {
    // console.log(kratosPublicURL());
    console.log(backendUrl());
    fetch(`${backendUrl()}/api/hello`, {
      headers: { Connection: "keep-alive" },
    })
      .then((response) => response.text())
      .then((data) => console.log(data));
  }

  return (
    <div className="w-[20vw] h-full bg-gray-100 flex flex-col items-center justify-between">
      <div className="flex flex-col items-center justify-start p-2 w-full gap-2">
        <div className="flex items-center justify-start p-2 w-full gap-4">
          <MountainSnow  size={44} />
          <span className="text-3xl font-bold text-center">Aerrus Cloud</span>
        </div>
        <div className="w-full p-3">
          <JobList />
        </div>
      </div>
      <div className="p-1 pt-2">
        <Button variant="destructive" onClick={() => hello()}>
          Test Endpoint
        </Button>
      </div>
    </div>
  );
}
