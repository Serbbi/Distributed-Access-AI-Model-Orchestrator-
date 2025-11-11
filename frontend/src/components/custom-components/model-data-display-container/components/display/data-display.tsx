import { FileText, Trash2 } from "lucide-react";
import { BaseItemDisplay } from "./display";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { backendUrl } from "@/config";

export default function DataDisplay({
  title,
  description,
  id: dataId
}: Omit<BaseItemDisplay, "type">) {
  async function handleDelete() {
    const response = await fetch(`${backendUrl()}/api/timeseries/delete`, {
      credentials: "include",
      method: "POST",
      headers: {
        Accept: "application/json",
      },
      body: JSON.stringify({ dataId }),
    });

    if (response.ok) {
      console.log("Data deleted successfully");
    } else {
      console.log("Failed to delete data")
    }
  }

  return (
    <div className="flex items-center justify-center flex-col w-[20%] h-[20%] bg-gray-100 rounded-md text-gray-500 font-bold p-3">
      <Dialog>
        <DialogTrigger>
          <FileText size={128} className="text-gray-300" /> {title}
        </DialogTrigger>
        <DialogContent onOpenAutoFocus={(e) => e.preventDefault()}>
          <DialogHeader>
            <DialogTitle className="flex flex-row w-full justify-start items-center gap-2">
              <Badge className="flex items-center justify-between gap-1 text-sm font-light">
                <FileText size={16} /> Data
              </Badge>
              {title}
            </DialogTitle>
          </DialogHeader>

          <div className="flex flex-col gap-2">
            <div className="text-sm text-muted-foreground">{description}</div>
          </div>

          <DialogFooter>
            <Button
              variant="destructive"
              className="font-light"
              onClick={handleDelete}
            >
              <Trash2 /> Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
