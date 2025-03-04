import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./components/ThemeProvider"; // Import the custom ThemeProvider
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import StudyActivities from "./pages/StudyActivities.jsx";
import StudyActivityShow from "./pages/StudyActivityShow.jsx";
import StudyActivityLaunch from "./pages/StudyActivityLaunch.jsx";
import Words from "./pages/Words.jsx";
import WordShow from "./pages/WordShow.jsx";
import Groups from "./pages/Groups.jsx";
import GroupShow from "./pages/GroupShow.jsx";
import StudySessions from "./pages/StudySessions.jsx";
import StudySessionShow from "./pages/StudySessionShow.jsx";
import Settings from "./pages/Settings.jsx";
import NotFound from "./pages/NotFound.jsx";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider> {/* Use the custom ThemeProvider */}
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="study_activities" element={<StudyActivities />} />
              <Route path="study_activities/:id" element={<StudyActivityShow />} />
              <Route path="study_activities/:id/launch" element={<StudyActivityLaunch />} />
              <Route path="words" element={<Words />} />
              <Route path="words/:id" element={<WordShow />} />
              <Route path="groups" element={<Groups />} />
              <Route path="groups/:id" element={<GroupShow />} />
              <Route path="study_sessions" element={<StudySessions />} />
              <Route path="study_sessions/:id" element={<StudySessionShow />} />
              <Route path="settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;