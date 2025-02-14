
import { useQuery } from "@tanstack/react-query";
import { getDashboardLastStudySession, getDashboardStudyProgress, getDashboardQuickStats } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { BookOpen, Check, Users, Zap } from "lucide-react";

const Dashboard = () => {
  const navigate = useNavigate();
  
  const { data: lastSession } = useQuery({
    queryKey: ["lastStudySession"],
    queryFn: getDashboardLastStudySession,
  });

  const { data: progress } = useQuery({
    queryKey: ["studyProgress"],
    queryFn: getDashboardStudyProgress,
  });

  const { data: stats } = useQuery({
    queryKey: ["quickStats"],
    queryFn: getDashboardQuickStats,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Button size="lg" onClick={() => navigate("/study_activities")}>
          Start Studying
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <Check className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.success_rate}%</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Study Sessions</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_study_sessions}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Groups</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_active_groups}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Study Streak</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.study_streak_days} days</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Last Study Session</CardTitle>
          </CardHeader>
          <CardContent>
            {lastSession && (
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">Group</div>
                <div className="font-medium">{lastSession.group_name}</div>
                <div className="text-sm text-muted-foreground">Date</div>
                <div className="font-medium">
                  {new Date(lastSession.created_at).toLocaleDateString()}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Study Progress</CardTitle>
          </CardHeader>
          <CardContent>
            {progress && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Total Words Studied</span>
                  <span className="font-medium">
                    {progress.total_words_studied} / {progress.total_available_words}
                  </span>
                </div>
                <div className="h-2 rounded-full bg-secondary">
                  <div
                    className="h-2 rounded-full bg-primary transition-all"
                    style={{
                      width: `${(progress.total_words_studied / progress.total_available_words) * 100}%`,
                    }}
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
