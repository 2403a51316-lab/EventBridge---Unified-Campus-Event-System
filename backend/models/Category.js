const mongoose = require('mongoose');

/**
 * Category Schema
 * Represents campus event classifications (e.g., Technical, Cultural, Sports, Workshop, Seminar).
 * Referenced by Event schema to support filtering, categorization, and analytical aggregation.
 */
const categorySchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, 'Category name is required'],
      unique: true,
      trim: true,
      minlength: [2, 'Category name must be at least 2 characters']
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model('Category', categorySchema);
