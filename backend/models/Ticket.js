const mongoose = require('mongoose');

/**
 * Ticket Schema
 * Represents the official digital entry pass issued upon successful event registration.
 * 
 * Referenced Data:
 * - registration: ObjectId referencing 'Registration' collection (unique 1-to-1 relationship).
 *   Why: Strict 1-to-1 relationship between an accepted registration and an issued physical/digital pass.
 *   If a registration is cancelled, the ticket can be invalidated.
 * 
 * Fields:
 * - ticketId: Alphanumeric unique readable code (e.g., 'EVT-1023-A7') used for manual check-in lookup.
 * - qrCodeDataUrl: Base64 data URL encoded QR image containing validation payload (ticketId, eventId, studentId).
 * - isCheckedIn: Boolean flag preventing duplicate entry scans at the venue gate.
 * - checkedInAt: Timestamp recorded when the organizer performs check-in.
 */
const ticketSchema = new mongoose.Schema(
  {
    registration: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Registration',
      required: [true, 'Registration reference is required'],
      unique: true
    },
    ticketId: {
      type: String,
      required: [true, 'Ticket ID code is required'],
      unique: true,
      trim: true,
      uppercase: true
    },
    qrCodeDataUrl: {
      type: String,
      required: [true, 'QR code data URL is required']
    },
    isCheckedIn: {
      type: Boolean,
      default: false
    },
    checkedInAt: {
      type: Date,
      default: null
    }
  },
  {
    timestamps: true
  }
);

// Additional performance indexes (ticketId and registration already have unique indexes from field definitions)
ticketSchema.index({ isCheckedIn: 1 });

module.exports = mongoose.model('Ticket', ticketSchema);
