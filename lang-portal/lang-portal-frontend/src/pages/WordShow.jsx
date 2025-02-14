
import { useQuery } from "@tanstack/react-query";
import { useParams, useNavigate } from "react-router-dom";
import { getWord } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const WordShow = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: word } = useQuery({
    queryKey: ["word", id],
    queryFn: () => getWord(id),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Word Details</h1>
      {word && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Word Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm text-muted-foreground">Marathi</div>
                <div className="text-2xl font-bold">{word.marathi}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Phonetic</div>
                <div className="text-xl">{word.phonetic}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">English</div>
                <div className="text-xl">{word.english}</div>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Study Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="text-sm text-muted-foreground">Correct Count</div>
                  <div className="text-2xl font-bold text-green-600">
                    {word.stats.correct_count}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Wrong Count</div>
                  <div className="text-2xl font-bold text-red-600">
                    {word.stats.wrong_count}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Groups</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {word.groups.map((group) => (
                    <Badge
                      key={group.id}
                      className="cursor-pointer"
                      onClick={() => navigate(`/groups/${group.id}`)}
                    >
                      {group.name}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

export default WordShow;
