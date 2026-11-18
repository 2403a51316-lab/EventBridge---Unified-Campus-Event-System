const mongoose = require('mongoose');

/**
 * Event Schema
 * Represents campus events created by organizers and submitted for admin approval.
 * 
 * Referenced Data:
 * - organizer: ObjectId referencing 'User' collection (must have role 'organizer' or 'admin').
 *   Why: Links event lifecycle directly to responsible club/department head for auditability,
 *   editing privileges, and organizer-specific dashboard views.
 * 
 * - category: ObjectId referencing 'Category' collection.
 *   Why: Decouples category taxonomy from event records. Allows standardized filtering
 *   (e.g., Technical, Cultural, Sports) and aggregation metrics without spelling drift.
 * 
 * Indexes:
 * - { status: 1 }: Frequent filtering for APPROVED events on student portal and PENDING on admin portal.
 * - { eventDate: 1 }: Sorting chronological upcoming/past events and calendar views.
 * - { category: 1 }: Fast index-backed filtering when students search by event genre.
 * - Compound { status: 1, eventDate: 1 }: Optimizes student query for "APPROVED upcoming events".
 */
const eventSchema = new mongoose.Schema(
  {
    organizer: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: [true, 'Event organizer is required']
    },
    category: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Category',
      required: [true, 'Event category is required']
    },
    title: {
      type: String,
      required: [true, 'Event title is required'],
      trim: true,
      minlength: [3, 'Title must be at least 3 characters'],
      maxlength: [120, 'Title cannot exceed 120 characters']
    },
    description: {
      type: String,
      required: [true, 'Event description is required'],
      trim: true
    },
    venue: {
      type: String,
      required: [true, 'Event venue is required'],
      trim: true
    },
    eventDate: {
      type: Date,
      required: [true, 'Event date and time is required']
    },
    seatLimit: {
      type: Number,
      required: [true, 'Seat limit is required'],
      min: [1, 'Seat limit must be at least 1']
    },
    registeredCount: {
      type: Number,
      default: 0,
      min: [0, 'Registered count cannot be negative']
    },
    status: {
      type: String,
      enum: ['PENDING', 'APPROVED', 'REJECTED', 'CANCELLED'],
      default: 'PENDING'
    },
    rejectionReason: {
      type: String,
      default: '',
      trim: true
    },
    createdAt: {
      type: Date,
      default: Date.now
    }
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Virtual property to calculate available seats dynamically
eventSchema.virtual('seatsLeft').get(function () {
  return Math.max(0, this.seatLimit - (this.registeredCount || 0));
});

// Virtual property to determine if event has already passed
eventSchema.virtual('isPast').get(function () {
  return new Date(this.eventDate) < new Date();
});

// Virtual property to determine if event is completely booked
eventSchema.virtual('isFull').get(function () {
  return (this.registeredCount || 0) >= this.seatLimit;
});

// Performance & Filtering Indexes
eventSchema.index({ status: 1 });
eventSchema.index({ eventDate: 1 });
eventSchema.index({ category: 1 });
eventSchema.index({ status: 1, eventDate: 1 });

module.exports = mongoose.model('Event', eventSchema);
