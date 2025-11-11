import { Bot, Play } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";
import { BaseItemDisplay } from "./display";
import { backendUrl } from "@/config";

interface Props extends Omit<BaseItemDisplay, "type"> {
  data: BaseItemDisplay[];
}

export default function ModelDisplay({
  title,
  description,
  id: modelId,
  data,
}: Props) {
  const [selection, setSelection] = useState<string | null>(null);

  const options = data.map((dataItem) => {
    return { name: dataItem.title, value: dataItem.id };
  });

  const startJob = async () => {
    if (!selection) {
      return;
    }
    const response = await fetch(
      `${backendUrl()}/api/train/execute?modelId=${modelId}&dataId=${selection}`,
      {
        method: "GET",
        credentials: "include",
        headers: {
          Accept: "application/json",
        },
      }
    );

    if (response.ok) {
      console.log("Job started.");
    }
  };

  return (
    <div className="flex items-center justify-center flex-col w-[20%] h-[20%] bg-gray-100 rounded-md text-gray-500 font-bold p-3">
      <Dialog>
        <DialogTrigger>
          <Bot size={128} className="text-gray-300" />
          {title}
        </DialogTrigger>
        <DialogContent onOpenAutoFocus={(e) => e.preventDefault()}>
          <DialogHeader>
            <DialogTitle className="flex flex-row w-full justify-start items-center gap-2">
              <Badge className="flex items-center justify-between gap-1 text-sm font-light">
                <Bot size={16} /> Model
              </Badge>
              {title}
            </DialogTitle>
          </DialogHeader>

          <div className="text-sm text-muted-foreground">{description}</div>

          <div className="flex flex-col gap-2">
            <div className="text-sm text-muted-foreground">
              Please select the data to use for model training.
            </div>
            <Select
              onValueChange={(value) => setSelection(value)}
              value={selection ?? undefined}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select model data..." />
              </SelectTrigger>
              <SelectContent>
                {options.map((option) => {
                  return (
                    <SelectItem key={option.value} value={option.value}>
                      {option.name}
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
          </div>

          <DialogFooter>
            <Button
              variant="default"
              className="font-light"
              disabled={!selection}
              onClick={startJob}
            >
              <Play />
              Run
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
