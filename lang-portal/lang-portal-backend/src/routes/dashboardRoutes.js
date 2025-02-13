const express = require('express');
const router = express.Router();
const { dashboardController } = require('../controllers/dashboardController');

router.get('/last_study_session', dashboardController.getLastStudySession);
router.get('/study_progress', dashboardController.getStudyProgress);
router.get('/quick-stats', dashboardController.getQuickStats);

module.exports = router;