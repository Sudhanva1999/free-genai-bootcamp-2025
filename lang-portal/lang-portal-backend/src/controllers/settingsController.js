const db = require('../database');

const settingsController = {
  async resetHistory(req, res) {
    try {
      await db.run('DELETE FROM word_review_items');
      await db.run('DELETE FROM study_sessions');
      await db.run('DELETE FROM word_reviews');
      
      res.json({
        success: true,
        message: 'Study history has been reset'
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async fullReset(req, res) {
    try {
      await db.run('DELETE FROM word_review_items');
      await db.run('DELETE FROM study_sessions');
      await db.run('DELETE FROM word_reviews');
      await db.run('DELETE FROM word_groups');
      await db.run('DELETE FROM words');
      await db.run('DELETE FROM groups');
      
      // Re-run migrations and seeds here
      // This would typically be handled by your migration system
      
      res.json({
        success: true,
        message: 'System has been fully reset'
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
};

module.exports = {
    settingsController
  };