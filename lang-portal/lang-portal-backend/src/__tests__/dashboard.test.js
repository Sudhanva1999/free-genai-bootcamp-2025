const { dashboardController } = require('../controllers/dashboardController');
const { Dashboard } = require('../models/dashboard');

// Mock the Dashboard model
jest.mock('../models/dashboard');

describe('Dashboard Controller', () => {
  let mockRequest;
  let mockResponse;
  
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup mock request and response
    mockRequest = {};
    mockResponse = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis(),
    };
  });

  describe('getLastStudySession', () => {
    it('should return last study session data when successful', async () => {
      const mockSession = {
        id: 123,
        group_id: 456,
        created_at: "2025-02-08T17:20:23-05:00",
        study_activity_id: 789,
        group_name: "Basic Greetings"
      };

      Dashboard.getLastStudySession.mockResolvedValue(mockSession);

      await dashboardController.getLastStudySession(mockRequest, mockResponse);

      expect(Dashboard.getLastStudySession).toHaveBeenCalled();
      expect(mockResponse.json).toHaveBeenCalledWith(mockSession);
    });

    it('should return empty object when no session exists', async () => {
      Dashboard.getLastStudySession.mockResolvedValue(null);

      await dashboardController.getLastStudySession(mockRequest, mockResponse);

      expect(Dashboard.getLastStudySession).toHaveBeenCalled();
      expect(mockResponse.json).toHaveBeenCalledWith({});
    });

    it('should handle errors appropriately', async () => {
      const error = new Error('Database error');
      Dashboard.getLastStudySession.mockRejectedValue(error);

      await dashboardController.getLastStudySession(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('getStudyProgress', () => {
    it('should return study progress data when successful', async () => {
      const mockProgress = {
        total_words_studied: 3,
        total_available_words: 124
      };

      Dashboard.getStudyProgress.mockResolvedValue(mockProgress);

      await dashboardController.getStudyProgress(mockRequest, mockResponse);

      expect(Dashboard.getStudyProgress).toHaveBeenCalled();
      expect(mockResponse.json).toHaveBeenCalledWith(mockProgress);
    });

    it('should handle errors appropriately', async () => {
      const error = new Error('Database error');
      Dashboard.getStudyProgress.mockRejectedValue(error);

      await dashboardController.getStudyProgress(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('getQuickStats', () => {
    it('should return quick stats data when successful', async () => {
      const mockStats = {
        success_rate: 80.0,
        total_study_sessions: 4,
        total_active_groups: 3,
        study_streak_days: 4
      };

      Dashboard.getQuickStats.mockResolvedValue(mockStats);

      await dashboardController.getQuickStats(mockRequest, mockResponse);

      expect(Dashboard.getQuickStats).toHaveBeenCalled();
      expect(mockResponse.json).toHaveBeenCalledWith(mockStats);
    });

    it('should handle errors appropriately', async () => {
      const error = new Error('Database error');
      Dashboard.getQuickStats.mockRejectedValue(error);

      await dashboardController.getQuickStats(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });
});