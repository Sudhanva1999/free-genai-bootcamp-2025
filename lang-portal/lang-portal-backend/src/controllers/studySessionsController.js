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
    const { id: sessionId } = req.params;
    const { word, correct } = req.body;
  
    try {
      // Find the word ID using the word name
      const wordId = await db.get("SELECT id FROM words WHERE name = ?", [word]);
  
      if (!wordId) {
        return res.status(404).json({ error: "Word not found" });
      }
  
      const wordIdValue = wordId.id;
  
      // Insert into word_review_items
      await db.run(
        `INSERT INTO word_review_items (word_id, study_session_id, correct)
        VALUES (?, ?, ?)`,
        [wordIdValue, sessionId, correct]
      );
  
      // Update word_reviews table
      await db.run(
        `INSERT INTO word_reviews (word_id, correct_count, wrong_count)
        VALUES (?, CASE WHEN ? THEN 1 ELSE 0 END, CASE WHEN ? THEN 0 ELSE 1 END)
        ON CONFLICT(word_id) DO UPDATE SET
        correct_count = correct_count + CASE WHEN ? THEN 1 ELSE 0 END,
        wrong_count = wrong_count + CASE WHEN ? THEN 0 ELSE 1 END`,
        [wordIdValue, correct, correct, correct, correct]
      );
  
      res.json({
        success: true,
        word,
        word_id: wordIdValue,
        study_session_id: parseInt(sessionId),
        correct,
        created_at: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async reviewWordInBody(req, res) {
    const { id: sessionId } = req.params;
    const { word, correct } = req.body;
  
    if (!word || typeof correct !== 'boolean') {
      return res.status(400).json({ error: "Missing required fields: word and correct" });
    }
  
    try {
      // Find the word ID using the word name
      const wordId = await db.get("SELECT id FROM words WHERE name = ?", [word]);
  
      if (!wordId) {
        // If word is not found, create it
        const result = await db.run("INSERT INTO words (name) VALUES (?)", [word]);
        const wordIdValue = result.lastID;
        
        // Insert into word_review_items
        await db.run(
          `INSERT INTO word_review_items (word_id, study_session_id, correct)
          VALUES (?, ?, ?)`,
          [wordIdValue, sessionId, correct]
        );
  
        // Update word_reviews table
        await db.run(
          `INSERT INTO word_reviews (word_id, correct_count, wrong_count)
          VALUES (?, CASE WHEN ? THEN 1 ELSE 0 END, CASE WHEN ? THEN 0 ELSE 1 END)
          ON CONFLICT(word_id) DO UPDATE SET
          correct_count = correct_count + CASE WHEN ? THEN 1 ELSE 0 END,
          wrong_count = wrong_count + CASE WHEN ? THEN 0 ELSE 1 END`,
          [wordIdValue, correct, correct, correct, correct]
        );
  
        return res.json({
          success: true,
          word,
          word_id: wordIdValue,
          study_session_id: parseInt(sessionId),
          correct,
          created_at: new Date().toISOString()
        });
      }
  
      const wordIdValue = wordId.id;
  
      // Insert into word_review_items
      await db.run(
        `INSERT INTO word_review_items (word_id, study_session_id, correct)
        VALUES (?, ?, ?)`,
        [wordIdValue, sessionId, correct]
      );
  
      // Update word_reviews table
      await db.run(
        `INSERT INTO word_reviews (word_id, correct_count, wrong_count)
        VALUES (?, CASE WHEN ? THEN 1 ELSE 0 END, CASE WHEN ? THEN 0 ELSE 1 END)
        ON CONFLICT(word_id) DO UPDATE SET
        correct_count = correct_count + CASE WHEN ? THEN 1 ELSE 0 END,
        wrong_count = wrong_count + CASE WHEN ? THEN 0 ELSE 1 END`,
        [wordIdValue, correct, correct, correct, correct]
      );
  
      res.json({
        success: true,
        word,
        word_id: wordIdValue,
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