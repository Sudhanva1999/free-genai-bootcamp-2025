const db = require('../database');

class StudyActivity {
  static async findById(id) {
    return await db.get(
      "SELECT id, name, url, preview_url as thumbnail_url FROM study_activities WHERE id = ?",
      [id]
    );
  }

  static async findAll() {
    return await db.all(
      "SELECT id, name, url, preview_url as thumbnail_url FROM study_activities"
    );
  }

  static async getStudySessions(activityId, page = 1, limit = 100) {
    const offset = (page - 1) * limit;
    const rows = await db.all(
      `SELECT ss.id, sa.name as activity_name, g.name as group_name,
        ss.created_at as start_time,
        (SELECT MAX(created_at) FROM word_review_items 
         WHERE study_session_id = ss.id) as end_time,
        (SELECT COUNT(*) FROM word_review_items 
         WHERE study_session_id = ss.id) as review_items_count
      FROM study_sessions ss
      JOIN study_activities sa ON ss.study_activity_id = sa.id
      JOIN groups g ON ss.group_id = g.id
      WHERE sa.id = ?
      ORDER BY ss.created_at DESC
      LIMIT ? OFFSET ?`,
      [activityId, limit, offset]
    );

    const total = await db.get(
      "SELECT COUNT(*) as count FROM study_sessions WHERE study_activity_id = ?",
      [activityId]
    );

    return {
      items: rows,
      pagination: {
        current_page: page,
        total_pages: Math.ceil(total.count / limit),
        total_items: total.count,
        items_per_page: limit,
      },
    };
  }
}

module.exports = {
  StudyActivity,
};
