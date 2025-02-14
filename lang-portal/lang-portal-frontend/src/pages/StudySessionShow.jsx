
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { getStudySession, getStudySessionWords } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const StudySessionShow = () => {
  const { id } = useParams();

  const { data: session } = useQuery({
    queryKey: ["studySession", id],
    queryFn: () => getStudySession(id),
  });

  const { data: words } = useQuery({
    queryKey: ["studySessionWords", id],
    queryFn: () => getStudySessionWords(id),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Study Session Details</h1>

      {session && (
        <Card>
          <CardHeader>
            <CardTitle>Session Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <div className="text-sm text-muted-foreground">Activity</div>
                <div className="font-medium">{session.activity_name}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Group</div>
                <div className="font-medium">{session.group_name}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Start Time</div>
                <div className="font-medium">
                  {new Date(session.start_time).toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">End Time</div>
                <div className="font-medium">
                  {new Date(session.end_time).toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">
                  Review Items Count
                </div>
                <div className="font-medium">{session.review_items_count}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Words Reviewed</CardTitle>
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
        </CardContent>
      </Card>
    </div>
  );
};

export default StudySessionShow;
