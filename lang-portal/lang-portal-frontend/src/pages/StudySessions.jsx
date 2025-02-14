
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { getStudySessions } from "../services/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const StudySessions = () => {
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const { data } = useQuery({
    queryKey: ["studySessions", page],
    queryFn: () => getStudySessions(page),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Study Sessions</h1>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Activity</TableHead>
              <TableHead>Group</TableHead>
              <TableHead>Start Time</TableHead>
              <TableHead>End Time</TableHead>
              <TableHead>Items</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.map((session) => (
              <TableRow
                key={session.id}
                className="cursor-pointer"
                onClick={() => navigate(`/study_sessions/${session.id}`)}
              >
                <TableCell>{session.id}</TableCell>
                <TableCell>{session.activity_name}</TableCell>
                <TableCell>{session.group_name}</TableCell>
                <TableCell>
                  {new Date(session.start_time).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {new Date(session.end_time).toLocaleDateString()}
                </TableCell>
                <TableCell>{session.review_items_count}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {data?.pagination && (
        <div className="flex justify-center space-x-2">
          <Button
            variant="outline"
            onClick={() => setPage(page - 1)}
            disabled={page === 1}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            onClick={() => setPage(page + 1)}
            disabled={page === data.pagination.total_pages}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
};

export default StudySessions;
