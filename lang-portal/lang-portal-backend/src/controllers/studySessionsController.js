const { StudySession } = require('../models/studySession');
const db = require('../database');

const studySessionsController = {
  async index(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const result = await StudySession.findAll(page);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async show(req, res) {
    try {
      const session = await StudySession.findById(req.params.id);
      if (!session) {
        return res.status(404).json({ error: 'Study session not found' });
      }
      res.json(session);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async getSessionWords(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const result = await StudySession.getSessionWords(req.params.id, page);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async reviewWord(req, res) {
    const { id: sessionId, word_id: wordId } = req.params;
    const { correct } = req.body;

    try {
      await db.run(
        `INSERT INTO word_review_items (word_id, study_session_id, correct)
        VALUES (?, ?, ?)`,
        [wordId, sessionId, correct]
      );

      // Update word_reviews table
      await db.run(
        `INSERT INTO word_reviews (word_id, correct_count, wrong_count)
        VALUES (?, CASE WHEN ? THEN 1 ELSE 0 END, CASE WHEN ? THEN 0 ELSE 1 END)
        ON CONFLICT(word_id) DO UPDATE SET
        correct_count = correct_count + CASE WHEN ? THEN 1 ELSE 0 END,
        wrong_count = wrong_count + CASE WHEN ? THEN 0 ELSE 1 END`,
        [wordId, correct, correct, correct, correct]
      );

      res.json({
        success: true,
        word_id: parseInt(wordId),
        study_session_id: parseInt(sessionId),
        correct,
        created_at: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
};

module.exports = {
    studySessionsController
  };