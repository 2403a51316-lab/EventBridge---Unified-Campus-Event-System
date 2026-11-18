const mongoose = require('mongoose');

/**
 * Department Schema
 * Represents academic departments (e.g., Computer Science, Mechanical Engineering, MBA).
 * Referenced by User (to denote student/organizer department) and displayed across the campus portal.
 */
const departmentSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, 'Department name is required'],
      unique: true,
      trim: true,
      minlength: [2, 'Department name must be at least 2 characters']
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model('Department', departmentSchema);
