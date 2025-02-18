const { settingsController } = require('../controllers/settingsController');
const db = require('../database');

// Mock the database module
jest.mock('../database');

describe('Settings Controller', () => {
  let mockRequest;
  let mockResponse;
  
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup mock request and response
    mockRequest = {};
    mockResponse = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis()
    };

    // Setup database mock
    db.run.mockReset();
    db.run.mockResolvedValue();
  });

  describe('resetHistory', () => {
    it('should delete all study history when successful', async () => {
      await settingsController.resetHistory(mockRequest, mockResponse);

      // Verify all expected DELETE queries were executed
      expect(db.run).toHaveBeenCalledTimes(3);
      expect(db.run).toHaveBeenCalledWith('DELETE FROM word_review_items');
      expect(db.run).toHaveBeenCalledWith('DELETE FROM study_sessions');
      expect(db.run).toHaveBeenCalledWith('DELETE FROM word_reviews');

      // Verify response
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: true,
        message: 'Study history has been reset'
      });
    });

    it('should handle database errors appropriately', async () => {
      const error = new Error('Database error');
      db.run.mockRejectedValueOnce(error);

      await settingsController.resetHistory(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });

    it('should stop execution if any query fails', async () => {
      const error = new Error('Database error');
      db.run.mockRejectedValueOnce(error);

      await settingsController.resetHistory(mockRequest, mockResponse);

      // Should only have attempted the first query
      expect(db.run).toHaveBeenCalledTimes(1);
    });
  });

  describe('fullReset', () => {
    it('should delete all data when successful', async () => {
      await settingsController.fullReset(mockRequest, mockResponse);

      // Verify all expected DELETE queries were executed
      expect(db.run).toHaveBeenCalledTimes(6);
      expect(db.run).toHaveBeenCalledWith('DELETE FROM word_review_items');
      expect(db.run).toHaveBeenCalledWith('DELETE FROM study_sessions');
      expect(db.run).toHaveBeenCalledWith('DELETE FROM word_reviews');
      expect(db.run).toHaveBeenCalledWith('DELETE FROM word_groups');
      expect(db.run).toHaveBeenCalledWith('DELETE FROM words');
      expect(db.run).toHaveBeenCalledWith('DELETE FROM groups');

      // Verify response
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: true,
        message: 'System has been fully reset'
      });
    });

    it('should handle database errors appropriately', async () => {
      const error = new Error('Database error');
      db.run.mockRejectedValueOnce(error);

      await settingsController.fullReset(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });

    it('should stop execution if any query fails', async () => {
      const error = new Error('Database error');
      db.run.mockRejectedValueOnce(error);

      await settingsController.fullReset(mockRequest, mockResponse);

      // Should only have attempted the first query
      expect(db.run).toHaveBeenCalledTimes(1);
    });

    it('should execute DELETE queries in the correct order', async () => {
      await settingsController.fullReset(mockRequest, mockResponse);

      const calls = db.run.mock.calls.map(call => call[0]);
      
      // Verify order of operations (important for referential integrity)
      expect(calls).toEqual([
        'DELETE FROM word_review_items',
        'DELETE FROM study_sessions',
        'DELETE FROM word_reviews',
        'DELETE FROM word_groups',
        'DELETE FROM words',
        'DELETE FROM groups'
      ]);
    });
  });
});