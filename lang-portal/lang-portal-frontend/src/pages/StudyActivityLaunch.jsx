
import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getGroups, createStudyActivity } from "../services/api";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/components/ui/use-toast";

const StudyActivityLaunch = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedGroup, setSelectedGroup] = useState("");

  const { data: groups } = useQuery({
    queryKey: ["groups"],
    queryFn: () => getGroups(),
  });

  const handleLaunch = async () => {
    try {
      const result = await createStudyActivity({
        group_id: parseInt(selectedGroup),
        study_activity_id: parseInt(id),
      });
      toast({
        title: "Study activity launched",
        description: "Your study session has been created successfully.",
      });
      navigate(`/study_sessions/${result.id}`);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to launch study activity",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="mx-auto max-w-md space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Launch Study Activity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Select Group</label>
            <Select onValueChange={setSelectedGroup} value={selectedGroup}>
              <SelectTrigger>
                <SelectValue placeholder="Select a group" />
              </SelectTrigger>
              <SelectContent>
                {groups?.items.map((group) => (
                  <SelectItem key={group.id} value={group.id.toString()}>
                    {group.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button
            className="w-full"
            onClick={handleLaunch}
            disabled={!selectedGroup}
          >
            Launch Now
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default StudyActivityLaunch;
