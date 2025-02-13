const db = require('../database');

class StudySession {
  static async findAll(page = 1, limit = 100, filters = {}) {
    const offset = (page - 1) * limit;
    let query = `
      SELECT ss.id, sa.name as activity_name, g.name as group_name,
        ss.created_at as start_time,
        (SELECT MAX(created_at) FROM word_review_items 
         WHERE study_session_id = ss.id) as end_time,
        (SELECT COUNT(*) FROM word_review_items 
         WHERE study_session_id = ss.id) as review_items_count
      FROM study_sessions ss
      JOIN study_activities sa ON ss.study_activity_id = sa.id
      JOIN groups g ON ss.group_id = g.id
    `;

    const queryParams = [];

    // Add WHERE clause if groupId filter exists
    if (filters.groupId) {
      query += ' WHERE ss.group_id = ?';
      queryParams.push(filters.groupId);
    }

    // Add ORDER BY and LIMIT clauses
    query += ' ORDER BY ss.created_at DESC LIMIT ? OFFSET ?';
    queryParams.push(limit, offset);

    const rows = await db.all(query, queryParams);

    // Modify total count query based on filters
    let countQuery = 'SELECT COUNT(*) as count FROM study_sessions';
    const countParams = [];
    
    if (filters.groupId) {
      countQuery += ' WHERE group_id = ?';
      countParams.push(filters.groupId);
    }

    const total = await db.get(countQuery, countParams);

    return {
      items: rows || [], // Ensure we always return an array
      pagination: {
        current_page: page,
        total_pages: Math.ceil((total?.count || 0) / limit),
        total_items: total?.count || 0,
        items_per_page: limit,
      },
    };
  }

  static async findById(id) {
    const result = await db.get(
      `SELECT ss.id, sa.name as activity_name, g.name as group_name,
        ss.created_at as start_time,
        (SELECT MAX(created_at) FROM word_review_items 
         WHERE study_session_id = ss.id) as end_time,
        (SELECT COUNT(*) FROM word_review_items 
         WHERE study_session_id = ss.id) as review_items_count
      FROM study_sessions ss
      JOIN study_activities sa ON ss.study_activity_id = sa.id
      JOIN groups g ON ss.group_id = g.id
      WHERE ss.id = ?`,
      [id]
    );
    return result || null;
  }

  static async getSessionWords(sessionId, page = 1, limit = 100) {
    const offset = (page - 1) * limit;
    const rows = await db.all(
      `SELECT w.*, 
        SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END) as correct_count,
        SUM(CASE WHEN wri.correct = 0 THEN 1 ELSE 0 END) as wrong_count
      FROM words w
      JOIN word_review_items wri ON w.id = wri.word_id
      WHERE wri.study_session_id = ?
      GROUP BY w.id
      LIMIT ? OFFSET ?`,
      [sessionId, limit, offset]
    );

    const total = await db.get(
      "SELECT COUNT(DISTINCT word_id) as count FROM word_review_items WHERE study_session_id = ?",
      [sessionId]
    );

    return {
      items: rows || [],
      pagination: {
        current_page: page,
        total_pages: Math.ceil((total?.count || 0) / limit),
        total_items: total?.count || 0,
        items_per_page: limit,
      },
    };
  }

  static async create(groupId, studyActivityId) {
    const result = await db.run(
      "INSERT INTO study_sessions (group_id, study_activity_id) VALUES (?, ?)",
      [groupId, studyActivityId]
    );
    return { id: result.lastID, group_id: groupId };
  }
}

module.exports = {
  StudySession,
};