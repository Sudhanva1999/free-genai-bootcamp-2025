
import { useQuery } from "@tanstack/react-query";
import { useParams, useNavigate } from "react-router-dom";
import { getStudyActivity, getStudyActivitySessions } from "../services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const StudyActivityShow = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: activity } = useQuery({
    queryKey: ["studyActivity", id],
    queryFn: () => getStudyActivity(id),
  });

  const { data: sessions } = useQuery({
    queryKey: ["studyActivitySessions", id],
    queryFn: () => getStudyActivitySessions(id),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">{activity?.name}</h1>
        <Button onClick={() => navigate(`/study_activities/${id}/launch`)}>
          Launch Activity
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Activity Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <img
            src={activity?.thumbnail_url}
            alt={activity?.name}
            className="aspect-video w-full rounded-lg object-cover"
          />
          <p className="text-muted-foreground">{activity?.description}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Past Study Sessions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sessions?.items.map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between rounded-lg border p-4"
              >
                <div>
                  <div className="font-medium">{session.group_name}</div>
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
        </CardContent>
      </Card>
    </div>
  );
};

export default StudyActivityShow;
