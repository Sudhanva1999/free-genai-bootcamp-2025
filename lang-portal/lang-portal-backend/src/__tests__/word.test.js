const { wordsController } = require('../controllers/wordController');
const { Word } = require('../models/words');

// Mock the Word model
jest.mock('../models/words');

describe('Words Controller', () => {
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
        total_pages: 5,
        total_items: 500,
        items_per_page: 100
      }
    };

    it('should return paginated words when successful', async () => {
      Word.findAll.mockResolvedValue(mockWords);

      await wordsController.index(mockRequest, mockResponse);

      expect(Word.findAll).toHaveBeenCalledWith(1);
      expect(mockResponse.json).toHaveBeenCalledWith(mockWords);
    });

    it('should handle custom page parameter', async () => {
      mockRequest.query.page = '2';
      Word.findAll.mockResolvedValue({
        ...mockWords,
        pagination: { ...mockWords.pagination, current_page: 2 }
      });

      await wordsController.index(mockRequest, mockResponse);

      expect(Word.findAll).toHaveBeenCalledWith(2);
    });

    it('should use default page 1 for invalid page numbers', async () => {
      mockRequest.query.page = 'invalid';
      Word.findAll.mockResolvedValue(mockWords);

      await wordsController.index(mockRequest, mockResponse);

      expect(Word.findAll).toHaveBeenCalledWith(1);
    });

    it('should handle errors appropriately', async () => {
      const error = new Error('Database error');
      Word.findAll.mockRejectedValue(error);

      await wordsController.index(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });
  });

  describe('show', () => {
    const mockWord = {
      marathi: "नमस्कार",
      phonetic: "Namaskāra",
      english: "hello",
      stats: {
        correct_count: 5,
        wrong_count: 2
      },
      groups: [
        {
          id: 1,
          name: "Basic Greetings"
        }
      ]
    };

    it('should return word details when found', async () => {
      mockRequest.params.id = '1';
      Word.findById.mockResolvedValue(mockWord);

      await wordsController.show(mockRequest, mockResponse);

      expect(Word.findById).toHaveBeenCalledWith('1');
      expect(mockResponse.json).toHaveBeenCalledWith(mockWord);
    });

    it('should return 404 when word not found', async () => {
      mockRequest.params.id = '999';
      Word.findById.mockResolvedValue(null);

      await wordsController.show(mockRequest, mockResponse);

      expect(Word.findById).toHaveBeenCalledWith('999');
      expect(mockResponse.status).toHaveBeenCalledWith(404);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: 'Word not found' });
    });

    it('should handle errors appropriately', async () => {
      mockRequest.params.id = '1';
      const error = new Error('Database error');
      Word.findById.mockRejectedValue(error);

      await wordsController.show(mockRequest, mockResponse);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({ error: error.message });
    });

    it('should include group information in word details', async () => {
      mockRequest.params.id = '1';
      Word.findById.mockResolvedValue(mockWord);

      await wordsController.show(mockRequest, mockResponse);

      const responseData = mockResponse.json.mock.calls[0][0];
      expect(responseData.groups).toBeDefined();
      expect(responseData.groups).toBeInstanceOf(Array);
      expect(responseData.groups[0]).toHaveProperty('id');
      expect(responseData.groups[0]).toHaveProperty('name');
    });

    it('should format statistics correctly', async () => {
      mockRequest.params.id = '1';
      Word.findById.mockResolvedValue(mockWord);

      await wordsController.show(mockRequest, mockResponse);

      const responseData = mockResponse.json.mock.calls[0][0];
      expect(responseData.stats).toBeDefined();
      expect(responseData.stats).toHaveProperty('correct_count');
      expect(responseData.stats).toHaveProperty('wrong_count');
    });
  });
});