const express = require('express');
const router = express.Router();
const { groupsController } = require('../controllers/groupsController');

router.get('/', groupsController.index);
router.get('/:id', groupsController.show);
router.get('/:id/words', groupsController.getGroupWords);
router.get('/:id/study_sessions', groupsController.getStudySessions);

module.exports = router;