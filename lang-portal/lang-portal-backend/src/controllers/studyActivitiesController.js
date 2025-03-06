const { StudyActivity } = require('../models/studyActivity');
const { StudySession } = require('../models/studySession');


const studyActivitiesController = {
  async show(req, res) {
    try {
      const activity = await StudyActivity.findById(req.params.id);
      if (!activity) {
        return res.status(404).json({ error: 'Study activity not found' });
      }
      res.json(activity);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async showAll(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const result = await StudyActivity.findAll(page);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async getStudySessions(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const result = await StudyActivity.getStudySessions(req.params.id, page);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async create(req, res) {
    try {
        const group_id = req.query.group_id;
        const study_activity_id = req.query.study_activity_id;
      const result = await StudySession.create(group_id, study_activity_id);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
};

module.exports = {
    studyActivitiesController
  };