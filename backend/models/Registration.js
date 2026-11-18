const mongoose = require('mongoose');

/**
 * Registration Schema
 * Connects a Student to an Event for participation tracking.
 * 
 * Referenced Data:
 * - event: ObjectId referencing 'Event' collection.
 *   Why: Links the reservation to specific event details, venue, and seat tally.
 * 
 * - student: ObjectId referencing 'User' collection (role 'student').
 *   Why: Links the reservation to student identity, email notifications, and personal tickets.
 * 
 * Unique Compound Index:
 * - { event: 1, student: 1 }: Enforces at the database engine level that a student
 *   can only hold ONE registration per event. Prevents duplicate booking attempts.
 */
const registrationSchema = new mongoose.Schema(
  {
    event: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Event',
      required: [true, 'Event reference is required']
    },
    student: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: [true, 'Student reference is required']
    },
    status: {
      type: String,
      enum: ['REGISTERED', 'CANCELLED'],
      default: 'REGISTERED'
    },
    registeredAt: {
      type: Date,
      default: Date.now
    }
  },
  {
    timestamps: true
  }
);

// Enforce unique registration per student per event
registrationSchema.index({ event: 1, student: 1 }, { unique: true });

// Optimize query for fetching all registrations of a student or all attendees of an event
registrationSchema.index({ student: 1, status: 1 });
registrationSchema.index({ event: 1, status: 1 });

module.exports = mongoose.model('Registration', registrationSchema);
