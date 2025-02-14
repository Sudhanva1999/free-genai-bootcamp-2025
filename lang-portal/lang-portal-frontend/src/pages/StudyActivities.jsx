
import { useQuery } from "@tanstack/react-query";
import { getStudyActivities } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

const StudyActivities = () => {
  const navigate = useNavigate();
  const { data } = useQuery({
    queryKey: ["studyActivities"],
    queryFn: getStudyActivities,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Study Activities</h1>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {data?.map((activity) => (
          <Card key={activity.id}>
            <CardHeader>
              <CardTitle>{activity.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <img
                src={activity.thumbnail_url}
                alt={activity.name}
                className="aspect-video w-full rounded-lg object-cover"
              />
              <p className="text-sm text-muted-foreground">{activity.description}</p>
              <div className="flex space-x-2">
                <Button onClick={() => navigate(`/study_activities/${activity.id}/launch`)}>
                  Launch
                </Button>
                <Button variant="outline" onClick={() => navigate(`/study_activities/${activity.id}`)}>
                  View Details
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default StudyActivities;
