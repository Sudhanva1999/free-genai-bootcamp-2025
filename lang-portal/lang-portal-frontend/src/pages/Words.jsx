
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { getWords } from "../services/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const Words = () => {
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const { data } = useQuery({
    queryKey: ["words", page],
    queryFn: () => getWords(page),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Words</h1>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Marathi</TableHead>
              <TableHead>Phonetic</TableHead>
              <TableHead>English</TableHead>
              <TableHead>Correct Count</TableHead>
              <TableHead>Wrong Count</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.map((word) => (
              <TableRow
                key={word.marathi}
                className="cursor-pointer"
                onClick={() => navigate(`/words/${word.id}`)}
              >
                <TableCell>{word.marathi}</TableCell>
                <TableCell>{word.phonetic}</TableCell>
                <TableCell>{word.english}</TableCell>
                <TableCell>{word.correct_count}</TableCell>
                <TableCell>{word.wrong_count}</TableCell>
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

export default Words;
