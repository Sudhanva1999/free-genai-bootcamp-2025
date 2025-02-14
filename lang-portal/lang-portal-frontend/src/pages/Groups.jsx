
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { getGroups } from "../services/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const Groups = () => {
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const { data } = useQuery({
    queryKey: ["groups", page],
    queryFn: () => getGroups(page),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Groups</h1>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Word Count</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.map((group) => (
              <TableRow
                key={group.id}
                className="cursor-pointer"
                onClick={() => navigate(`/groups/${group.id}`)}
              >
                <TableCell className="font-medium">{group.name}</TableCell>
                <TableCell>{group.word_count}</TableCell>
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

export default Groups;
