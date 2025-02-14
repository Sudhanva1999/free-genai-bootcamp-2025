const db = require('../database');

class Dashboard {
  static async getLastStudySession() {
    return await db.get(
      `SELECT ss.id, ss.group_id, ss.created_at,
          ss.study_activity_id, g.name as group_name
        FROM study_sessions ss
        JOIN groups g ON ss.group_id = g.id
        ORDER BY ss.created_at DESC
        LIMIT 1`
    );
  }

  static async getStudyProgress() {
    const totalWords = await db.get("SELECT COUNT(*) as count FROM words");
    const studiedWords = await db.get(
      "SELECT COUNT(DISTINCT word_id) as count FROM word_review_items"
    );

    return {
      total_words_studied: studiedWords.count,
      total_available_words: totalWords.count,
    };
  }

  static async getQuickStats() {
    const totalSessions = await db.get(
      "SELECT COUNT(*) as count FROM study_sessions"
    );

    const activeGroups = await db.get(
      "SELECT COUNT(DISTINCT group_id) as count FROM study_sessions"
    );

    const success = await db.get(
      `SELECT 
          ROUND(AVG(CASE WHEN correct = 1 THEN 100 ELSE 0 END), 1) as rate
        FROM word_review_items`
    );

    const streak = await db.get(
      `WITH RECURSIVE dates(date) AS (
          SELECT date(min(created_at))
          FROM study_sessions
          UNION ALL
          SELECT date(date, '+1 day')
          FROM dates
          WHERE date < date('now')
        )
        SELECT COUNT(*) as days
        FROM dates d
        WHERE EXISTS (
          SELECT 1 FROM study_sessions ss
          WHERE date(ss.created_at) = d.date
        )`
    );

    return {
      success_rate: success.rate || 0,
      total_study_sessions: totalSessions.count || 0,
      total_active_groups: activeGroups.count || 0,
      study_streak_days: streak.days || 0,
    };
  }
}

module.exports = {
  Dashboard,
};
