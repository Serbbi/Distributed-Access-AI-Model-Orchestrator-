"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { backendUrl } from "@/config";
import { Bot, FileText, Plus } from "lucide-react";
import { useState } from "react";

export function UploadDialog() {
  const [selection, setSelection] = useState<'model' | 'data' | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const formData = new FormData();
      formData.append("file", e.target.files[0]);

      const endpoint = selection === 'data' ? "timeseries/upload" : "files/upload";

      const response = await fetch(`${backendUrl()}/api/${endpoint}`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        console.log("File uploaded successfully");
      }
    }
  };

  return (
    <Dialog
      onOpenChange={() => {
        setSelection(null);
      }}
    >
      <DialogTrigger asChild disabled>
        <Button variant="secondary">
          <Plus />
          Upload
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Model Or Data</DialogTitle>
        </DialogHeader>
        <div className="flex gap-8 flex-col">
          <div className="flex flex-col w-full align-start items-start gap-1">
            <div className="text-gray-600">
              1. Please select the type of upload
            </div>
            <ToggleGroup
              type="single"
              variant="outline"
              onValueChange={(selection) => setSelection(selection as 'model' | 'data')}
            >
              <ToggleGroupItem value="model">
                <Bot className="h-4 w-4" /> Model
              </ToggleGroupItem>
              <ToggleGroupItem value="data">
                <FileText className="h-4 w-4" /> Data
              </ToggleGroupItem>
            </ToggleGroup>
          </div>

          <div className="flex flex-col w-full align-start items-start gap-1">
            <div className="text-gray-600">
              {`2. Please select ${
                selection
                  ? selection === "data"
                    ? "data"
                    : "a model"
                  : "a file"
              } to upload`}
            </div>
            <Input
              disabled={selection === null}
              id="file-upload"
              type="file"
              accept={".zip"}
              onChange={handleFileUpload}
            />
            <div className="text-gray-600 text-xs">
              {selection &&
                `Supported file types: ${
                  selection === "data" ? ".csv" : ".zip"
                }`}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button>Continue</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
