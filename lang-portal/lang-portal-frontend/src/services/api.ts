
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:3000/api",
});

export const getDashboardLastStudySession = () =>
  api.get("/dashboard/last_study_session").then((res) => res.data);

export const getDashboardStudyProgress = () =>
  api.get("/dashboard/study_progress").then((res) => res.data);

export const getDashboardQuickStats = () =>
  api.get("/dashboard/quick-stats").then((res) => res.data);

export const getStudyActivities = () =>
  api.get("/study_activities").then((res) => res.data);

export const getStudyActivity = (id: string) =>
  api.get(`/study_activities/${id}`).then((res) => res.data);

export const getStudyActivitySessions = (id: string) =>
  api.get(`/study_activities/${id}/study_sessions`).then((res) => res.data);

export const createStudyActivity = (data: { group_id: number; study_activity_id: number }) =>
  api.post("/study_activities", data).then((res) => res.data);

export const getWords = (page = 1) =>
  api.get(`/words?page=${page}`).then((res) => res.data);

export const getWord = (id: string) =>
  api.get(`/words/${id}`).then((res) => res.data);

export const getGroups = (page = 1) =>
  api.get(`/groups?page=${page}`).then((res) => res.data);

export const getGroup = (id: string) =>
  api.get(`/groups/${id}`).then((res) => res.data);

export const getGroupWords = (id: string, page = 1) =>
  api.get(`/groups/${id}/words?page=${page}`).then((res) => res.data);

export const getGroupStudySessions = (id: string, page = 1) =>
  api.get(`/groups/${id}/study_sessions?page=${page}`).then((res) => res.data);

export const getStudySessions = (page = 1) =>
  api.get(`/study_sessions?page=${page}`).then((res) => res.data);

export const getStudySession = (id: string) =>
  api.get(`/study_sessions/${id}`).then((res) => res.data);

export const getStudySessionWords = (id: string, page = 1) =>
  api.get(`/study_sessions/${id}/words?page=${page}`).then((res) => res.data);

export const resetHistory = () =>
  api.post("/reset_history").then((res) => res.data);

export const fullReset = () =>
  api.post("/full_reset").then((res) => res.data);

export const reviewWord = (studySessionId: number, wordId: number, correct: boolean) =>
  api.post(`/study_sessions/${studySessionId}/words/${wordId}/review`, { correct }).then((res) => res.data);
