const express = require('express');
const router = express.Router();
const { wordsController } = require('../controllers/wordController');

router.get('/', wordsController.index);
router.get('/:id', wordsController.show);

module.exports = router;