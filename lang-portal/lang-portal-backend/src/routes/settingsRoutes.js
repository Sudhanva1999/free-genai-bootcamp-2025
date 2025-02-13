const express = require('express');
const router = express.Router();
const { settingsController } = require('../controllers/settingsController');

router.post('/reset_history', settingsController.resetHistory);
router.post('/full_reset', settingsController.fullReset);

module.exports = router;