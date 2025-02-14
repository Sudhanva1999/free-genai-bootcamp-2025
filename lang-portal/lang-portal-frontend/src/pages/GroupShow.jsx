
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { getGroup, getGroupWords, getGroupStudySessions } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const GroupShow = () => {
  const { id } = useParams();
  const [wordsPage, setWordsPage] = useState(1);
  const [sessionsPage, setSessionsPage] = useState(1);

  const { data: group } = useQuery({
    queryKey: ["group", id],
    queryFn: () => getGroup(id),
  });

  const { data: words } = useQuery({
    queryKey: ["groupWords", id, wordsPage],
    queryFn: () => getGroupWords(id, wordsPage),
  });

  const { data: sessions } = useQuery({
    queryKey: ["groupSessions", id, sessionsPage],
    queryFn: () => getGroupStudySessions(id, sessionsPage),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">{group?.name}</h1>

      <Card>
        <CardHeader>
          <CardTitle>Group Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {group?.stats.total_word_count} Words
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Words in Group</CardTitle>
        </CardHeader>
        <CardContent>
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
              {words?.items.map((word) => (
                <TableRow key={word.marathi}>
                  <TableCell>{word.marathi}</TableCell>
                  <TableCell>{word.phonetic}</TableCell>
                  <TableCell>{word.english}</TableCell>
                  <TableCell>{word.correct_count}</TableCell>
                  <TableCell>{word.wrong_count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {words?.pagination && (
            <div className="mt-4 flex justify-center space-x-2">
              <Button
                variant="outline"
                onClick={() => setWordsPage(wordsPage - 1)}
                disabled={wordsPage === 1}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                onClick={() => setWordsPage(wordsPage + 1)}
                disabled={wordsPage === words.pagination.total_pages}
              >
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Study Sessions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sessions?.items.map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between rounded-lg border p-4"
              >
                <div>
                  <div className="font-medium">{session.activity_name}</div>
                  <div className="text-sm text-muted-foreground">
                    {new Date(session.start_time).toLocaleDateString()}
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">
                  {session.review_items_count} items
                </div>
              </div>
            ))}
          </div>
          {sessions?.pagination && (
            <div className="mt-4 flex justify-center space-x-2">
              <Button
                variant="outline"
                onClick={() => setSessionsPage(sessionsPage - 1)}
                disabled={sessionsPage === 1}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                onClick={() => setSessionsPage(sessionsPage + 1)}
                disabled={sessionsPage === sessions.pagination.total_pages}
              >
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default GroupShow;
