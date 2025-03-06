const express = require('express');
const router = express.Router();
const { studySessionsController } = require('../controllers/studySessionsController');

router.get('/', studySessionsController.index);
router.get('/:id', studySessionsController.show);
router.get('/:id/words', studySessionsController.getSessionWords);
router.post('/:id/words/:word/review', studySessionsController.reviewWord);
router.post('/:id/words/review', studySessionsController.reviewWordInBody);


module.exports = router;