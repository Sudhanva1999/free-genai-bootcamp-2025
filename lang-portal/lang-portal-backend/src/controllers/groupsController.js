const { Group } = require("../models/group");
const { StudySession } = require("../models/studySession");

const groupsController = {
  async index(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const result = await Group.findAll(page);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async show(req, res) {
    try {
      const group = await Group.findById(req.params.id);
      if (!group) {
        return res.status(404).json({ error: "Group not found" });
      }
      res.json(group);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async getGroupWords(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const result = await Group.getGroupWords(req.params.id, page);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },

  async getStudySessions(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const groupId = parseInt(req.params.id);
      
      const result = await StudySession.findAll(page, 100, { groupId });
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  },
};

module.exports = {
  groupsController,
};
