"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  CircleCheck,
  FileText,
  LoaderCircle,
  Play,
  Router,
  XCircle,
} from "lucide-react";
import SockJS from "sockjs-client";
import { Stomp, IFrame, IMessage } from "@stomp/stompjs";
import { backendUrl } from "@/config";
import { useState } from "react";

type Status = "RUNNING" | "SUCCESS" | "FAILURE";

interface Job {
  title: string;
  id: string;
  status: Status;
}

function getStatusIcon(status: Status) {
  switch (status) {
    case "RUNNING":
      return (
        <Badge className="flex justify-start gap-2 w-fit text-sm font-light">
          <LoaderCircle size={14} className="text-gray-400 animate-spin" />
          Ongoing
        </Badge>
      );
    case "SUCCESS":
      return (
        <Badge className="flex justify-start gap-2 w-fit text-sm font-light">
          <CircleCheck size={14} className="text-green-400" /> Complete
        </Badge>
      );
    default:
      return (
        <Badge className="flex justify-start gap-2 w-fit text-sm font-light">
          <XCircle size={14} className="text-red-400" /> Canceled
        </Badge>
      );
  }
}

export function JobList() {
  const socket = new SockJS(`${backendUrl()}/api/ws`);
  const [jobs, setJobs] = useState<Job[]>([]);
  const stompClient = Stomp.over(socket);

  stompClient.connect({}, function (frame: IFrame) {
    console.log("Connected: " + frame);

    stompClient.subscribe("/topic/logs", function (message: IMessage) {
      const data = JSON.parse(message.body);
      console.log("Message received:", data.metadata.status);
      if (data.id !== null) {
        setJobs((prev) => {
          const exists = prev.some((job) => job.id === data.id);
          if (exists) {
            return prev.map((job) =>
              job.id === data.id
                ? {
                    ...job,
                    status: data.metadata.status,
                  }
                : job
            );
          } else {
            return [
              ...prev,
              {
                id: data.id,
                title:
                  data.id.length > 10 ? data.id.slice(0, 10) + "…" : data.id,
                status: data.metadata.status,
              },
            ];
          }
        });
      }
    });
  });
  // jobs = [
  //   { id: "1", title: "ICNN Predictor", status: "Running" },
  //   { id: "2", title: "ICNN Predictor", status: "Completed" },
  //   { id: "3", title: "ICNN Predictor", status: "Failed" },
  // ];

  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Status</TableHead>
            <TableHead>ID</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {jobs.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={2}
                className="text-center text-muted-foreground py-6"
              >
                No jobs to display.
              </TableCell>
            </TableRow>
          ) : (
            jobs.map((job) => (
              <Dialog key={job.id}>
                <DialogTrigger asChild>
                  <TableRow className="odd:bg-muted/50 cursor-pointer hover:bg-gray-200">
                    <TableCell>{getStatusIcon(job.status)}</TableCell>
                    <TableCell>{job.title}</TableCell>
                  </TableRow>
                </DialogTrigger>
                <DialogContent onOpenAutoFocus={(e) => e.preventDefault()}>
                  <DialogHeader>
                    <DialogTitle className="flex flex-row w-full justify-start items-center gap-2">
                      <Badge className="flex items-center justify-between gap-1 text-sm font-light">
                        <Router size={16} /> Job
                      </Badge>
                      {getStatusIcon(job.status)}
                      {job.id}
                    </DialogTitle>
                  </DialogHeader>
                  <div className="flex justify-end gap-2">
                    <Button variant="default" className="font-light" disabled>
                      <FileText />
                      {["FAILURE", "TIMEOUT"].includes(job.status)
                        ? "View Logs"
                        : "View Output"}
                    </Button>
                    <Button variant="default" className="font-light" disabled>
                      <Play />
                      Run
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
