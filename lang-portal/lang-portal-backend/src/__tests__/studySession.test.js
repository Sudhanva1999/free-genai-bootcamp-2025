const { studySessionsController } = require('../controllers/studySessionsController');
const { StudySession } = require('../models/studySession');
const db = require('../database');

// Mock the model and database
jest.mock('../models/studySession');
jest.mock('../database');

describe('Study Sessions Controller', () => {
  let mockRequest;
  let mockResponse;
  
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup mock request and response
    mockRequest = {
      query: {},
      params: {},
      body: {}
    };
    mockResponse = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis()
    };

    // Setup database mock
    db.run.mockReset();
    db.run.mockResolvedValue();
  });

  describe('index', () => {
    const mockSessions = {
      items: [
        {
          id: 123,
          activity_name: "Vocabulary Quiz",
          group_name: "Basic Greetings",
          start_time: "2025-02-08T17:20:23-05:00",
          end_time: "2025-02-08T17:30:23-05:00",
          review_items_count: 20
        }
      ],
      pagination: {
        current_page: 1,
        total_pages: 5,
        total_items: 100,
        items_per_page: 100
      }
    };

    it('should return paginated study sessions when successful', async () => {
      StudySession.findAll.mockResolvedValue(mockSessions);

      await studySessionsController.index(mockRequest, mockResponse);

      expect(StudySession.findAll).toHaveBeenCalledWith(1);
      expect(mockResponse.json).toHaveBeenCalledWith(mockSessions);
    });

    it('should handle custom page parameter', async () => {
      mockRequest.query.page = '2';
      StudySession.findAll.mockResolvedValue(mockSessions);

      await studySessionsController.index(mockRequest, mockResponse);

      expect(StudySession.findAll).toHaveBeenCalledWith(2);
    });

    it('should handle errors appropriately', async () => {
      const error = new Error('Database error');
      StudySession.findAll.mockRejectedValue(error);

      await studySessionsController.index(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('show', () => {
    const mockSession = {
      id: 123,
      activity_name: "Vocabulary Quiz",
      group_name: "Basic Greetings",
      start_time: "2025-02-08T17:20:23-05:00",
      end_time: "2025-02-08T17:30:23-05:00",
      review_items_count: 20
    };

    it('should return study session when found', async () => {
      mockRequest.params.id = '123';
      StudySession.findById.mockResolvedValue(mockSession);

      await studySessionsController.show(mockRequest, mockResponse);

      expect(StudySession.findById).toHaveBeenCalledWith('123');
      expect(mockResponse.json).toHaveBeenCalledWith(mockSession);
    });

    it('should return 404 when session not found', async () => {
      mockRequest.params.id = '999';
      StudySession.findById.mockResolvedValue(null);

      await studySessionsController.show(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(404);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: 'Study session not found' });
    });

    it('should handle errors appropriately', async () => {
      mockRequest.params.id = '123';
      const error = new Error('Database error');
      StudySession.findById.mockRejectedValue(error);

      await studySessionsController.show(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('getSessionWords', () => {
    const mockWords = {
      items: [
        {
          marathi: "नमस्कार",
          phonetic: "Namaskāra",
          english: "hello",
          correct_count: 5,
          wrong_count: 2
        }
      ],
      pagination: {
        current_page: 1,
        total_pages: 1,
        total_items: 20,
        items_per_page: 100
      }
    };

    it('should return session words when successful', async () => {
      mockRequest.params.id = '123';
      StudySession.getSessionWords.mockResolvedValue(mockWords);

      await studySessionsController.getSessionWords(mockRequest, mockResponse);

      expect(StudySession.getSessionWords).toHaveBeenCalledWith('123', 1);
      expect(mockResponse.json).toHaveBeenCalledWith(mockWords);
    });

    it('should handle custom page parameter', async () => {
      mockRequest.params.id = '123';
      mockRequest.query.page = '2';
      StudySession.getSessionWords.mockResolvedValue(mockWords);

      await studySessionsController.getSessionWords(mockRequest, mockResponse);

      expect(StudySession.getSessionWords).toHaveBeenCalledWith('123', 2);
    });

    it('should handle errors appropriately', async () => {
      mockRequest.params.id = '123';
      const error = new Error('Database error');
      StudySession.getSessionWords.mockRejectedValue(error);

      await studySessionsController.getSessionWords(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('reviewWord', () => {
    beforeEach(() => {
      // Mock the current date for consistent testing
      jest.useFakeTimers();
      jest.setSystemTime(new Date('2025-02-08T17:33:07-05:00'));
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should create word review when successful', async () => {
      mockRequest.params = { id: '123', word_id: '1' };
      mockRequest.body = { correct: true };

      await studySessionsController.reviewWord(mockRequest, mockResponse);

      // Verify word_review_items insertion (first call)
      expect(db.run).toHaveBeenNthCalledWith(1,
        `INSERT INTO word_review_items (word_id, study_session_id, correct)
        VALUES (?, ?, ?)`,
        ['1', '123', true]
      );

      // Verify word_reviews update (second call)
      expect(db.run).toHaveBeenNthCalledWith(2,
        `INSERT INTO word_reviews (word_id, correct_count, wrong_count)
        VALUES (?, CASE WHEN ? THEN 1 ELSE 0 END, CASE WHEN ? THEN 0 ELSE 1 END)
        ON CONFLICT(word_id) DO UPDATE SET
        correct_count = correct_count + CASE WHEN ? THEN 1 ELSE 0 END,
        wrong_count = wrong_count + CASE WHEN ? THEN 0 ELSE 1 END`,
        ['1', true, true, true, true]
      );

      // Verify word_reviews upsert
      expect(db.run).toHaveBeenCalledWith(
        expect.stringContaining('INSERT INTO word_reviews'),
        ['1', true, true, true, true]
      );

      // Verify response format matches API spec
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: true,
        word_id: 1,
        study_session_id: 123,
        correct: true,
        created_at: '2025-02-08T22:33:07.000Z'  // UTC format
      });
    });

    it('should handle incorrect reviews', async () => {
      mockRequest.params = { id: '123', word_id: '1' };
      mockRequest.body = { correct: false };

      await studySessionsController.reviewWord(mockRequest, mockResponse);

      // Verify first call - inserting review item
      expect(db.run).toHaveBeenNthCalledWith(1,
        `INSERT INTO word_review_items (word_id, study_session_id, correct)
        VALUES (?, ?, ?)`,
        ['1', '123', false]
      );

      // Verify second call - updating word statistics
      expect(db.run).toHaveBeenNthCalledWith(2,
        `INSERT INTO word_reviews (word_id, correct_count, wrong_count)
        VALUES (?, CASE WHEN ? THEN 1 ELSE 0 END, CASE WHEN ? THEN 0 ELSE 1 END)
        ON CONFLICT(word_id) DO UPDATE SET
        correct_count = correct_count + CASE WHEN ? THEN 1 ELSE 0 END,
        wrong_count = wrong_count + CASE WHEN ? THEN 0 ELSE 1 END`,
        ['1', false, false, false, false]
      );
    });

    it('should handle database errors appropriately', async () => {
      mockRequest.params = { id: '123', word_id: '1' };
      mockRequest.body = { correct: true };

      const error = new Error('Database error');
      db.run.mockRejectedValueOnce(error);

      await studySessionsController.reviewWord(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });

    it('should stop execution if first query fails', async () => {
      mockRequest.params = { id: '123', word_id: '1' };
      mockRequest.body = { correct: true };

      const error = new Error('Database error');
      db.run.mockRejectedValueOnce(error);

      await studySessionsController.reviewWord(mockRequest, mockResponse);

      // Should only have attempted the first query
      expect(db.run).toHaveBeenCalledTimes(1);
    });
  });
});