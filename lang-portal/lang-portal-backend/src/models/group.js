const db = require('../database');

class Group {
  static async findAll(page = 1, limit = 100) {
    const offset = (page - 1) * limit;
    const rows = await db.all(
      `SELECT g.*, COUNT(wg.word_id) as word_count
      FROM groups g
      LEFT JOIN word_groups wg ON g.id = wg.group_id
      GROUP BY g.id
      LIMIT ? OFFSET ?`,
      [limit, offset]
    );

    const total = await db.get("SELECT COUNT(*) as count FROM groups");

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

  static async findById(id) {
    const group = await db.get("SELECT * FROM groups WHERE id = ?", [id]);
    if (!group) return null;

    const wordCount = await db.get(
      "SELECT COUNT(*) as count FROM word_groups WHERE group_id = ?",
      [id]
    );

    return {
      ...group,
      stats: {
        total_word_count: wordCount.count,
      },
    };
  }

  static async getGroupWords(groupId, page = 1, limit = 100) {
    const offset = (page - 1) * limit;
    const rows = await db.all(
      `SELECT w.*, 
        COALESCE(wr.correct_count, 0) as correct_count,
        COALESCE(wr.wrong_count, 0) as wrong_count
      FROM words w
      JOIN word_groups wg ON w.id = wg.word_id
      LEFT JOIN word_reviews wr ON w.id = wr.word_id
      WHERE wg.group_id = ?
      LIMIT ? OFFSET ?`,
      [groupId, limit, offset]
    );

    const total = await db.get(
      "SELECT COUNT(*) as count FROM word_groups WHERE group_id = ?",
      [groupId]
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
  Group,
};
