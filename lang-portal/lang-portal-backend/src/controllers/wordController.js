
const { Word } = require('../models/words');

const wordsController = {
  async index(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const result = await Word.findAll(page);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async show(req, res) {
    try {
      const word = await Word.findById(req.params.id);
      if (!word) {
        return res.status(404).json({ error: 'Word not found' });
      }
      res.json(word);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
};

module.exports = {
  wordsController
};