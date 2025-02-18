const { groupsController } = require('../controllers/groupsController');
const { Group } = require('../models/group');
const { StudySession } = require('../models/studySession');

// Mock the models
jest.mock('../models/group');
jest.mock('../models/studySession');

describe('Groups Controller', () => {
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

  describe('index', () => {
    const mockPaginatedResult = {
      items: [
        { id: 1, name: "Basic Greetings", word_count: 20 }
      ],
      pagination: {
        current_page: 1,
        total_pages: 1,
        total_items: 1,
        items_per_page: 100
      }
    };

    it('should return paginated groups when successful', async () => {
      Group.findAll.mockResolvedValue(mockPaginatedResult);

      await groupsController.index(mockRequest, mockResponse);

      expect(Group.findAll).toHaveBeenCalledWith(1);
      expect(mockResponse.json).toHaveBeenCalledWith(mockPaginatedResult);
    });

    it('should handle custom page parameter', async () => {
      mockRequest.query.page = '2';
      Group.findAll.mockResolvedValue(mockPaginatedResult);

      await groupsController.index(mockRequest, mockResponse);

      expect(Group.findAll).toHaveBeenCalledWith(2);
    });

    it('should handle errors appropriately', async () => {
      const error = new Error('Database error');
      Group.findAll.mockRejectedValue(error);

      await groupsController.index(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('show', () => {
    const mockGroup = {
      id: 1,
      name: "Basic Greetings",
      stats: {
        total_word_count: 20
      }
    };

    it('should return group details when found', async () => {
      mockRequest.params.id = '1';
      Group.findById.mockResolvedValue(mockGroup);

      await groupsController.show(mockRequest, mockResponse);

      expect(Group.findById).toHaveBeenCalledWith('1');
      expect(mockResponse.json).toHaveBeenCalledWith(mockGroup);
    });

    it('should return 404 when group not found', async () => {
      mockRequest.params.id = '999';
      Group.findById.mockResolvedValue(null);

      await groupsController.show(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(404);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: 'Group not found' });
    });

    it('should handle errors appropriately', async () => {
      mockRequest.params.id = '1';
      const error = new Error('Database error');
      Group.findById.mockRejectedValue(error);

      await groupsController.show(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('getGroupWords', () => {
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
        total_items: 1,
        items_per_page: 100
      }
    };

    it('should return paginated group words when successful', async () => {
      mockRequest.params.id = '1';
      Group.getGroupWords.mockResolvedValue(mockWords);

      await groupsController.getGroupWords(mockRequest, mockResponse);

      expect(Group.getGroupWords).toHaveBeenCalledWith('1', 1);
      expect(mockResponse.json).toHaveBeenCalledWith(mockWords);
    });

    it('should handle custom page parameter', async () => {
      mockRequest.params.id = '1';
      mockRequest.query.page = '2';
      Group.getGroupWords.mockResolvedValue(mockWords);

      await groupsController.getGroupWords(mockRequest, mockResponse);

      expect(Group.getGroupWords).toHaveBeenCalledWith('1', 2);
    });

    it('should handle errors appropriately', async () => {
      mockRequest.params.id = '1';
      const error = new Error('Database error');
      Group.getGroupWords.mockRejectedValue(error);

      await groupsController.getGroupWords(mockRequest, mockResponse);

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
        total_pages: 1,
        total_items: 1,
        items_per_page: 100
      }
    };

    it('should return paginated study sessions when successful', async () => {
      mockRequest.params.id = '1';
      StudySession.findAll.mockResolvedValue(mockSessions);

      await groupsController.getStudySessions(mockRequest, mockResponse);

      expect(StudySession.findAll).toHaveBeenCalledWith(1, 100, { groupId: 1 });
      expect(mockResponse.json).toHaveBeenCalledWith(mockSessions);
    });

    it('should handle custom page parameter', async () => {
      mockRequest.params.id = '1';
      mockRequest.query.page = '2';
      StudySession.findAll.mockResolvedValue(mockSessions);

      await groupsController.getStudySessions(mockRequest, mockResponse);

      expect(StudySession.findAll).toHaveBeenCalledWith(2, 100, { groupId: 1 });
    });

    it('should handle errors appropriately', async () => {
      mockRequest.params.id = '1';
      const error = new Error('Database error');
      StudySession.findAll.mockRejectedValue(error);

      await groupsController.getStudySessions(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });
});