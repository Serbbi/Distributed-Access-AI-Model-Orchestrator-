"use client";

import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { useSearchContext } from "../../search-provider";

export default function SearchBar() {
  const { searchString, setSearch } = useSearchContext();

  return (
    <div className="relative w-full max-w-md">
      <Search
        className="-translate-y-1/2 text-gray-400 absolute left-3 top-1/2"
        size={18}
      />
      <Input
        type="text"
        placeholder="Search..."
        value={searchString}
        onChange={(e) => setSearch(e.target.value)}
        className="pl-10 pr-10 w-full border rounded-lg"
      />
    </div>
  );
}
