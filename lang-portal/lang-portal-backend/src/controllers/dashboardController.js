const { Dashboard } = require("../models/dashboard");

const dashboardController = {
  async getLastStudySession(req, res) {
    try {
      const session = await Dashboard.getLastStudySession();
      res.json(session || {});
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async getStudyProgress(req, res) {
    try {
      const progress = await Dashboard.getStudyProgress();
      res.json(progress);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async getQuickStats(req, res) {
    try {
      const stats = await Dashboard.getQuickStats();
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },
};

module.exports = {
  dashboardController,
};
