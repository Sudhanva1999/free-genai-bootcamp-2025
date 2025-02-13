// src/app.js
const express = require('express');
const cors = require('cors');
const dashboardRoutes = require('./routes/dashboardRoutes');
const wordsRoutes = require('./routes/wordRoutes');
const groupsRoutes = require('./routes/groupRoutes');
const studySessionsRoutes = require('./routes/studySessionRoutes');
const studyActivitiesRoutes = require('./routes/studyActivityRoutes');
const settingsRoutes = require('./routes/settingsRoutes');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// API Routes
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/words', wordsRoutes);
app.use('/api/groups', groupsRoutes);
app.use('/api/study_sessions', studySessionsRoutes);
app.use('/api/study_activities', studyActivitiesRoutes);
app.use('/api', settingsRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    message: 'The requested resource was not found'
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

module.exports = app;