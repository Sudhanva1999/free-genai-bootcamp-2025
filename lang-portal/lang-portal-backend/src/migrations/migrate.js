const fs = require('fs').promises;
const path = require('path');
const Database = require('better-sqlite3');

class DatabaseSetup {
    constructor(dbPath) {
        this.db = new Database(dbPath);
        this.sqlPath = path.join(__dirname, '../../sql/setup');
        this.seedPath = path.join(__dirname, '../../src/seeds');
    }

    async init() {
        try {
            // Execute all SQL setup scripts in order
            await this.executeSetupScripts();
            
            // Seed the database
            await this.seedDatabase();
            
            console.log('Database setup completed successfully');
        } catch (error) {
            console.error('Error during database setup:', error);
            throw error;
        }
    }

    async sql(filename) {
        const filePath = path.join(this.sqlPath, filename);
        return await fs.readFile(filePath, 'utf8');
    }

    async executeSetupScripts() {
        const setupScripts = [
            'create_table_words.sql',
            'create_table_word_reviews.sql',
            'create_table_word_review_items.sql',
            'create_table_groups.sql',
            'create_table_word_groups.sql',
            'create_table_study_activities.sql',
            'create_table_study_sessions.sql'
        ];

        for (const script of setupScripts) {
            const sqlContent = await this.sql(script);
            this.db.exec(sqlContent);
            console.log(`Executed ${script}`);
        }
    }

    async seedDatabase() {
        // Seed adjectives
        await this.seedWordGroup('data_adjectives.json', 1, 'data_adjectives');
        
        // Seed verbs
        await this.seedWordGroup('data_verbs.json', 2, 'data_verbs');
        
        // Seed study activities
        await this.seedStudyActivities();
    }

    async seedWordGroup(filename, groupId, groupName) {
        const filePath = path.join(this.seedPath, filename);
        const data = JSON.parse(await fs.readFile(filePath, 'utf8'));

        // Insert group
        const insertGroup = this.db.prepare(
            'INSERT INTO groups (id, name, words_count) VALUES (?, ?, 0)'
        );
        insertGroup.run(groupId, groupName);

        // Insert words and create relationships
        const insertWord = this.db.prepare(
            'INSERT INTO words (marathi, phonetic, english, parts) VALUES (?, ?, ?, ?)'
        );
        const insertWordGroup = this.db.prepare(
            'INSERT INTO word_groups (word_id, group_id) VALUES (?, ?)'
        );
        const updateWordCount = this.db.prepare(
            'UPDATE groups SET words_count = words_count + 1 WHERE id = ?'
        );

        // Use transaction for better performance and data consistency
        const transaction = this.db.transaction((words) => {
            for (const word of words) {
                const result = insertWord.run(
                    word.marathi,
                    word.phonetic,
                    word.english,
                    JSON.stringify(word.parts) // Convert parts array to JSON string
                );
                insertWordGroup.run(result.lastInsertRowid, groupId);
                updateWordCount.run(groupId);
            }
        });

        transaction(data);
        console.log(`Seeded ${data.length} words for group ${groupName}`);
    }

    async seedStudyActivities() {
        const filePath = path.join(this.seedPath, 'study_activities.json');
        const activities = JSON.parse(await fs.readFile(filePath, 'utf8'));

        const insertActivity = this.db.prepare(
            'INSERT INTO study_activities (name, url, preview_url) VALUES (?, ?, ?)'
        );

        const transaction = this.db.transaction((activities) => {
            for (const activity of activities) {
                insertActivity.run(
                    activity.name,
                    activity.url,
                    activity.preview_url
                );
            }
        });

        transaction(activities);
        console.log(`Seeded ${activities.length} study activities`);
    }

    close() {
        this.db.close();
    }
}

// Usage
async function main() {
    const dbSetup = new DatabaseSetup('words.db');
    try {
        await dbSetup.init();
    } finally {
        dbSetup.close();
    }
}

main().catch(console.error);