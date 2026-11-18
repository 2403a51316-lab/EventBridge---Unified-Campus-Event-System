const mongoose = require('mongoose');

/**
 * Connect to MongoDB database
 * Supports both local MongoDB instances and MongoDB Atlas cloud connection strings.
 */
const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI, {
      // Modern mongoose defaults are used; options kept clean
    });

    console.log(`[MongoDB Connected]: ${conn.connection.host}/${conn.connection.name}`);
  } catch (error) {
    console.error(`[MongoDB Connection Error]: ${error.message}`);
    console.warn('[Tip]: Ensure MongoDB is running locally (e.g. mongodb://127.0.0.1:27017/smart_campus_events) or provide a valid MongoDB Atlas URI in .env');
    // In production, exit process on failure. In dev, keep server up so static frontend is accessible for inspection.
    if (process.env.NODE_ENV === 'production') {
      process.exit(1);
    }
  }
};

module.exports = connectDB;
