import request from 'supertest';
import app from '../app'; 

describe('Study Sessions Controller', () => {
  it('should return the most recent study session', async () => {
    const response = await request(app).get('/api/dashboard/last_study_session');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({
      id: expect.any(Number),
      group_name: expect.any(String),
    });
  });

  it('should return study progress statistics', async () => {
    const response = await request(app).get('/api/dashboard/study_progress');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({
      total_words_studied: expect.any(Number),
      total_available_words: expect.any(Number),
    });
  });

  it('should return quick overview statistics', async () => {
    const response = await request(app).get('/api/dashboard/quick-stats');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({
      success_rate: expect.any(Number),
      study_streak_days: expect.any(Number),
    });
  });

  it('should return a specific study activity', async () => {
    const response = await request(app).get('/api/study_activities/1');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({
      id: expect.any(Number),
      description: expect.any(String),
    });
  });
});