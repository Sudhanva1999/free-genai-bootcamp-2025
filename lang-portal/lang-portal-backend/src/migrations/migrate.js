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
            await this.executeSetupScripts();
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
        await this.seedWordGroup('data_adjectives.json', 1, 'data_adjectives');
        await this.seedWordGroup('data_verbs.json', 2, 'data_verbs');
        await this.seedStudyActivities();
        await this.seedStudySessions();
        await this.seedWordReviews();
        await this.seedWordReviewItems();
    }

    async seedWordGroup(filename, groupId, groupName) {
        const filePath = path.join(this.seedPath, filename);
        const data = JSON.parse(await fs.readFile(filePath, 'utf8'));

        const insertGroup = this.db.prepare(
            'INSERT INTO groups (id, name, words_count) VALUES (?, ?, 0)'
        );
        insertGroup.run(groupId, groupName);

        const insertWord = this.db.prepare(
            'INSERT INTO words (marathi, phonetic, english, parts) VALUES (?, ?, ?, ?)'
        );
        const insertWordGroup = this.db.prepare(
            'INSERT INTO word_groups (word_id, group_id) VALUES (?, ?)'
        );
        const updateWordCount = this.db.prepare(
            'UPDATE groups SET words_count = words_count + 1 WHERE id = ?'
        );

        const transaction = this.db.transaction((words) => {
            for (const word of words) {
                const result = insertWord.run(
                    word.marathi,
                    word.phonetic,
                    word.english,
                    JSON.stringify(word.parts)
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

    async seedStudySessions() {
        const filePath = path.join(this.seedPath, 'study_sessions.json');
        const sessions = JSON.parse(await fs.readFile(filePath, 'utf8'));

        const insertSession = this.db.prepare(`
            INSERT INTO study_sessions (
                group_id,
                study_activity_id,
                created_at
            ) VALUES (?, ?, ?)
        `);

        const transaction = this.db.transaction((sessions) => {
            for (const session of sessions) {
                insertSession.run(
                    session.group_id,
                    session.study_activity_id,
                    session.created_at
                );
            }
        });

        transaction(sessions);
        console.log(`Seeded ${sessions.length} study sessions`);
    }

    async seedWordReviews() {
        const filePath = path.join(this.seedPath, 'word_reviews.json');
        const reviews = JSON.parse(await fs.readFile(filePath, 'utf8'));

        const insertReview = this.db.prepare(`
            INSERT INTO word_reviews (
                word_id,
                correct_count,
                wrong_count,
                last_reviewed
            ) VALUES (?, ?, ?, ?)
        `);

        const transaction = this.db.transaction((reviews) => {
            for (const review of reviews) {
                insertReview.run(
                    review.word_id,
                    review.correct_count,
                    review.wrong_count,
                    review.last_reviewed
                );
            }
        });

        transaction(reviews);
        console.log(`Seeded ${reviews.length} word reviews`);
    }

    async seedWordReviewItems() {
        const filePath = path.join(this.seedPath, 'word_review_items.json');
        const items = JSON.parse(await fs.readFile(filePath, 'utf8'));

        const insertItem = this.db.prepare(`
            INSERT INTO word_review_items (
                word_id,
                study_session_id,
                correct,
                created_at
            ) VALUES (?, ?, ?, ?)
        `);

        const transaction = this.db.transaction((items) => {
            for (const item of items) {
                insertItem.run(
                    item.word_id,
                    item.study_session_id,
                    item.correct ? 1 : 0, 
                    item.created_at
                );
            }
        });

        transaction(items);
        console.log(`Seeded ${items.length} word review items`);
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