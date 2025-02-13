const express = require('express');
const router = express.Router();
const { studyActivitiesController } = require('../controllers/studyActivitiesController');

router.get('/:id', studyActivitiesController.show);
router.get('/:id/study_sessions', studyActivitiesController.getStudySessions);
router.post('/', studyActivitiesController.create);

module.exports = router;