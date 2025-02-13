// src/database.js
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const path = require('path');

// Create a singleton database connection
let db = null;

async function getDb() {
  if (db) {
    return db;
  }

  db = await open({
    filename: path.join(__dirname, '../words.db'),
    driver: sqlite3.Database
  });

  return db;
}

// Export an object with async methods that get the db connection first
module.exports = {
  async all(sql, params = []) {
    const dbConn = await getDb();
    return await dbConn.all(sql, params);
  },

  async get(sql, params = []) {
    const dbConn = await getDb();
    return await dbConn.get(sql, params);
  },

  async run(sql, params = []) {
    const dbConn = await getDb();
    return await dbConn.run(sql, params);
  },

  async exec(sql) {
    const dbConn = await getDb();
    return await dbConn.exec(sql);
  }
};