"use client";

import { Menubar } from "../../ui/menubar";
import { UploadDialog } from "./components/upload-dialog";
import SearchBar from "./components/search-bar";
import { LogOut } from "lucide-react";
import { useSearchContext } from "../search-provider";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Button } from "@/components/ui/button";
import { backendUrl } from "@/config";

export default function AppBar() {
  const { setSearch, resetSearch } = useSearchContext();

  async function logout() {
    const res = await fetch(`${backendUrl()}/self-service/logout/browser`, {
      credentials: 'include',
    });

    const { logout_url } = await res.json();
    
    if (res.ok) {
      console.log(logout_url)
      window.location.href = logout_url;
    }
  }

  return (
    <Menubar className="absolute top-1 left-[calc(20%+8px)] w-[calc(80vw-16px)] bg-gray-100 h-[calc(text-4xl)]">
      <SearchBar />
      <div className="flex items-center justify-start w-full">
        <ToggleGroup
          type="single"
          variant="default"
          onValueChange={(value) => {
            if (value) {
              setSearch(value);
            } else {
              resetSearch();
            }
          }}
        >
          <ToggleGroupItem value="model">Models</ToggleGroupItem>
          <ToggleGroupItem value="data">Data</ToggleGroupItem>
        </ToggleGroup>
      </div>
      <div className="flex items-center justify-end w-full">
        <UploadDialog />
        <Button variant="secondary" onClick={logout}>
          <LogOut size={18} /> Logout
        </Button>
      </div>
    </Menubar>
  );
}
