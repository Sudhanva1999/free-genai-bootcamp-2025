const { studyActivitiesController } = require('../controllers/studyActivitiesController');
const { StudyActivity } = require('../models/studyActivity');
const { StudySession } = require('../models/studySession');

// Mock the models
jest.mock('../models/studyActivity');
jest.mock('../models/studySession');

describe('Study Activities Controller', () => {
  let mockRequest;
  let mockResponse;
  
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup mock request and response
    mockRequest = {
      query: {},
      params: {}
    };
    mockResponse = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis()
    };
  });

  describe('show', () => {
    const mockActivity = {
      id: 1,
      name: "Vocabulary Quiz",
      thumbnail_url: "https://example.com/thumbnail.jpg",
      description: "Practice your vocabulary with flashcards"
    };

    it('should return study activity when found', async () => {
      mockRequest.params.id = '1';
      StudyActivity.findById.mockResolvedValue(mockActivity);

      await studyActivitiesController.show(mockRequest, mockResponse);

      expect(StudyActivity.findById).toHaveBeenCalledWith('1');
      expect(mockResponse.json).toHaveBeenCalledWith(mockActivity);
    });

    it('should return 404 when activity not found', async () => {
      mockRequest.params.id = '999';
      StudyActivity.findById.mockResolvedValue(null);

      await studyActivitiesController.show(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(404);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: 'Study activity not found' });
    });

    it('should handle errors appropriately', async () => {
      mockRequest.params.id = '1';
      const error = new Error('Database error');
      StudyActivity.findById.mockRejectedValue(error);

      await studyActivitiesController.show(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('showAll', () => {
    const mockActivities = {
      items: [
        {
          id: 1,
          name: "Vocabulary Quiz",
          thumbnail_url: "https://example.com/thumbnail.jpg",
          description: "Practice your vocabulary with flashcards"
        }
      ],
      pagination: {
        current_page: 1,
        total_pages: 1,
        total_items: 1,
        items_per_page: 100
      }
    };

    it('should return paginated study activities when successful', async () => {
      StudyActivity.findAll.mockResolvedValue(mockActivities);

      await studyActivitiesController.showAll(mockRequest, mockResponse);

      expect(StudyActivity.findAll).toHaveBeenCalledWith(1);
      expect(mockResponse.json).toHaveBeenCalledWith(mockActivities);
    });

    it('should handle custom page parameter', async () => {
      mockRequest.query.page = '2';
      StudyActivity.findAll.mockResolvedValue(mockActivities);

      await studyActivitiesController.showAll(mockRequest, mockResponse);

      expect(StudyActivity.findAll).toHaveBeenCalledWith(2);
    });

    it('should handle errors appropriately', async () => {
      const error = new Error('Database error');
      StudyActivity.findAll.mockRejectedValue(error);

      await studyActivitiesController.showAll(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('getStudySessions', () => {
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
        items_per_page: 20
      }
    };

    it('should return study sessions when successful', async () => {
      mockRequest.params.id = '1';
      StudyActivity.getStudySessions.mockResolvedValue(mockSessions);

      await studyActivitiesController.getStudySessions(mockRequest, mockResponse);

      expect(StudyActivity.getStudySessions).toHaveBeenCalledWith('1', 1);
      expect(mockResponse.json).toHaveBeenCalledWith(mockSessions);
    });

    it('should handle custom page parameter', async () => {
      mockRequest.params.id = '1';
      mockRequest.query.page = '2';
      StudyActivity.getStudySessions.mockResolvedValue(mockSessions);

      await studyActivitiesController.getStudySessions(mockRequest, mockResponse);

      expect(StudyActivity.getStudySessions).toHaveBeenCalledWith('1', 2);
    });

    it('should handle errors appropriately', async () => {
      mockRequest.params.id = '1';
      const error = new Error('Database error');
      StudyActivity.getStudySessions.mockRejectedValue(error);

      await studyActivitiesController.getStudySessions(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('create', () => {
    const mockSession = {
      id: 124,
      group_id: 123
    };

    it('should create new study session when successful', async () => {
      mockRequest.query = {
        group_id: '123',
        study_activity_id: '456'
      };
      StudySession.create.mockResolvedValue(mockSession);

      await studyActivitiesController.create(mockRequest, mockResponse);

      expect(StudySession.create).toHaveBeenCalledWith('123', '456');
      expect(mockResponse.json).toHaveBeenCalledWith(mockSession);
    });

    it('should handle missing parameters', async () => {
      await studyActivitiesController.create(mockRequest, mockResponse);

      expect(StudySession.create).toHaveBeenCalledWith(undefined, undefined);
    });

    it('should handle errors appropriately', async () => {
      mockRequest.query = {
        group_id: '123',
        study_activity_id: '456'
      };
      const error = new Error('Database error');
      StudySession.create.mockRejectedValue(error);

      await studyActivitiesController.create(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });
});