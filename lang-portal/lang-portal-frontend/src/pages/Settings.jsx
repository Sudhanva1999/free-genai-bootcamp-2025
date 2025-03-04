import { useMutation } from "@tanstack/react-query";
import { resetHistory, fullReset } from "../services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTheme } from "../components/ThemeProvider"; // Import from your custom hook
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "@/components/ui/use-toast";

const Settings = () => {
  const { theme, setTheme, resolvedTheme } = useTheme();

  const resetHistoryMutation = useMutation({
    mutationFn: resetHistory,
    onSuccess: () => {
      toast({
        title: "History Reset",
        description: "Your study history has been reset successfully.",
      });
    },
  });

  const fullResetMutation = useMutation({
    mutationFn: fullReset,
    onSuccess: () => {
      toast({
        title: "Full Reset",
        description: "The system has been fully reset successfully.",
      });
    },
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>

      <Card>
        <CardHeader>
          <CardTitle>Theme</CardTitle>
        </CardHeader>
        <CardContent>
          <Select value={theme} onValueChange={(value) => setTheme(value)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select theme" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="light">Light</SelectItem>
              <SelectItem value="dark">Dark</SelectItem>
              <SelectItem value="system">System</SelectItem>
            </SelectContent>
          </Select>
          <p className="mt-2 text-sm text-muted-foreground">
            Current theme: {theme === "system" ? resolvedTheme : theme}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Reset Options</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Button
              variant="outline"
              onClick={() => resetHistoryMutation.mutate()}
              disabled={resetHistoryMutation.isPending}
            >
              Reset History
            </Button>
            <p className="mt-2 text-sm text-muted-foreground">
              This will delete all study sessions and word review items.
            </p>
          </div>
          <div>
            <Button
              variant="destructive"
              onClick={() => fullResetMutation.mutate()}
              disabled={fullResetMutation.isPending}
            >
              Full Reset
            </Button>
            <p className="mt-2 text-sm text-muted-foreground">
              This will drop all tables and re-create with seed data.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;