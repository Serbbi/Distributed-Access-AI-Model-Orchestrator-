"use client";

import { createContext, useContext, useState } from "react";

interface Props {
    children: React.ReactNode | React.ReactNode[];
}

interface SearchContextType {
  searchString: string;
  setSearch: (val: string) => void;
  resetSearch: () => void;
};

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider = ({ children }: Props) => {
  const [searchString, setSearchString] = useState("");

  return (
    <SearchContext.Provider
      value={{
        searchString,
        setSearch: setSearchString,
        resetSearch: () => setSearchString(""),
      }}
    >
      {children}
    </SearchContext.Provider>
  );
};

export const useSearchContext = () => {
  const context = useContext(SearchContext);
  if (!context) {
    throw new Error("useSearch must be used within a SearchProvider");
  } else {
    return context;
  }
};
