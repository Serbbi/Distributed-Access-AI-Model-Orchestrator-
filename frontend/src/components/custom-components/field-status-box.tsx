import { Check, Info, X } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";

type FieldStatus = "info" | "success" | "error";

interface Props {
  status: FieldStatus;
  message?: string;
}

function getStatusIcon(status: FieldStatus) {
  switch (status) {
    case "success":
      return <Check className="bg-green-200 text-green-700" />;
    case "error":
      return <X className="bg-red-200 text-red-700" />;
    case "info":
      return <Info className="bg-gray-200 text-gray-300" />;
  }
}

export function FieldStatusBox({ status, message }: Props) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger
          asChild
          className={`flex justify-center align-center fit rounded-[4px] outline ${
            status === "info"
              ? "outline-gray-300"
              : status === "success"
              ? "outline-green-700"
              : "outline-red-700"
          }`}
        >
          {getStatusIcon(status)}
        </TooltipTrigger>
        <TooltipContent>{message}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
