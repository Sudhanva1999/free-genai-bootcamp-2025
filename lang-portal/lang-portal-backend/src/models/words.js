// src/models/word.js
const db = require("../database");

class Word {
  static async findAll(page = 1, limit = 100) {
    const offset = (page - 1) * limit;
    const rows = await db.all(
      `SELECT w.*, 
        COALESCE(wr.correct_count, 0) as correct_count,
        COALESCE(wr.wrong_count, 0) as wrong_count
      FROM words w
      LEFT JOIN word_reviews wr ON w.id = wr.word_id
      LIMIT ? OFFSET ?`,
      [limit, offset]
    );

    const total = await db.get("SELECT COUNT(*) as count FROM words");

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
    const word = await db.get(
      `SELECT w.*, 
        COALESCE(wr.correct_count, 0) as correct_count,
        COALESCE(wr.wrong_count, 0) as wrong_count
      FROM words w
      LEFT JOIN word_reviews wr ON w.id = wr.word_id
      WHERE w.id = ?`,
      [id]
    );

    if (!word) return null;

    const groups = await db.all(
      `SELECT g.id, g.name
      FROM groups g
      JOIN word_groups wg ON g.id = wg.group_id
      WHERE wg.word_id = ?`,
      [id]
    );

    return {
      ...word,
      stats: {
        correct_count: word.correct_count,
        wrong_count: word.wrong_count,
      },
      groups,
    };
  }
}

module.exports = {
  Word,
};
