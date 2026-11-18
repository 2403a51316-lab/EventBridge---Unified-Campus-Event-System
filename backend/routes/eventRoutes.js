const crypto = require('crypto');
const express = require('express');
const QRCode = require('qrcode');
const Category = require('../models/Category');
const Event = require('../models/Event');
const Registration = require('../models/Registration');
const Ticket = require('../models/Ticket');
const { authenticateToken, authorizeRoles, requireApprovedOrganizer } = require('../middleware/auth');

const router = express.Router();
const defaultCategories = ['Technology', 'Culture', 'Sports', 'Workshop', 'Seminar'];

/**
 * GET /api/events
 * Public catalog of approved upcoming events
 */
router.get('/', async (req, res, next) => {
  try {
    const { category, search } = req.query;
    const filter = {
      status: 'APPROVED',
      eventDate: { $gte: new Date() }
    };

    if (category) {
      filter.category = category;
    }

    if (search) {
      const regex = new RegExp(search.trim(), 'i');
      filter.$or = [
        { title: regex },
        { description: regex },
        { venue: regex }
      ];
    }

    const events = await Event.find(filter)
      .populate('category', 'name')
      .populate('organizer', 'name organizationName')
      .sort({ eventDate: 1 });

    return res.status(200).json({ success: true, events });
  } catch (error) {
    return next(error);
  }
});

/**
 * GET /api/events/categories
 * Public endpoint to list event categories
 */
router.get('/categories', async (req, res, next) => {
  try {
    const categories = await Category.find().sort({ name: 1 });
    return res.status(200).json({ success: true, categories });
  } catch (error) {
    return next(error);
  }
});

/**
 * GET /api/events/:eventId
 * Public detail view for single event
 */
router.get('/:eventId/detail', async (req, res, next) => {
  try {
    const event = await Event.findById(req.params.eventId)
      .populate('category', 'name')
      .populate('organizer', 'name email organizationName');

    if (!event) {
      return res.status(404).json({ success: false, message: 'Event not found' });
    }

    return res.status(200).json({ success: true, event });
  } catch (error) {
    if (error.name === 'CastError') {
      return res.status(400).json({ success: false, message: 'Invalid event ID' });
    }
    return next(error);
  }
});

/**
 * POST /api/events
 * Organizer creates a new event (requires APPROVED organizer status)
 */
router.post('/', authenticateToken, authorizeRoles('organizer', 'admin'), requireApprovedOrganizer, async (req, res, next) => {
  try {
    const { title, description, venue, eventDate, seatLimit, category } = req.body;

    if (!title || !description || !venue || !eventDate || !seatLimit || !category) {
      return res.status(400).json({
        success: false,
        message: 'All event fields are required: title, description, venue, date, seat limit, and category'
      });
    }

    const date = new Date(eventDate);
    if (Number.isNaN(date.getTime()) || date <= new Date()) {
      return res.status(400).json({
        success: false,
        message: 'Please select a valid future event date and time'
      });
    }

    const seats = Number(seatLimit);
    if (!Number.isInteger(seats) || seats < 1) {
      return res.status(400).json({
        success: false,
        message: 'Seat limit must be a positive whole number (at least 1)'
      });
    }

    // Resolve category by ID or by Name
    let categoryRecord;
    if (category.match(/^[0-9a-fA-F]{24}$/)) {
      categoryRecord = await Category.findById(category);
    }
    if (!categoryRecord) {
      categoryRecord = await Category.findOneAndUpdate(
        { name: category },
        { $setOnInsert: { name: category } },
        { new: true, upsert: true }
      );
    }

    const event = await Event.create({
      organizer: req.user._id,
      category: categoryRecord._id,
      title: String(title).trim(),
      description: String(description).trim(),
      venue: String(venue).trim(),
      eventDate: date,
      seatLimit: seats,
      status: 'PENDING' // Always starts pending approval from admin
    });

    await event.populate('category', 'name');

    return res.status(201).json({
      success: true,
      message: 'Event proposal submitted successfully! It is now pending admin approval.',
      event
    });
  } catch (error) {
    if (error.name === 'ValidationError') {
      return res.status(400).json({
        success: false,
        message: Object.values(error.errors)[0]?.message || 'Invalid event details'
      });
    }
    return next(error);
  }
});

/**
 * GET /api/events/organizer/mine
 * Get events created by the logged-in organizer
 */
router.get('/organizer/mine', authenticateToken, authorizeRoles('organizer', 'admin'), async (req, res, next) => {
  try {
    const filter = req.user.role === 'admin' ? {} : { organizer: req.user._id };
    const events = await Event.find(filter)
      .populate('category', 'name')
      .sort({ createdAt: -1 });

    return res.status(200).json({ success: true, events });
  } catch (error) {
    return next(error);
  }
});

/**
 * GET /api/events/:eventId/registrations
 * Retrieve registered attendees for an event (Organizer or Admin)
 */
router.get('/:eventId/registrations', authenticateToken, authorizeRoles('organizer', 'admin'), async (req, res, next) => {
  try {
    const event = await Event.findById(req.params.eventId);
    if (!event) {
      return res.status(404).json({ success: false, message: 'Event not found' });
    }

    // Ensure organizer owns the event (unless admin)
    if (req.user.role === 'organizer' && event.organizer.toString() !== req.user._id.toString()) {
      return res.status(403).json({ success: false, message: 'You can only view attendees for your own events' });
    }

    const registrations = await Registration.find({ event: event._id })
      .populate('student', 'name email department phone')
      .sort({ registeredAt: -1 });

    // Also get ticket info (isCheckedIn status) for each registration
    const registrationIds = registrations.map(r => r._id);
    const tickets = await Ticket.find({ registration: { $in: registrationIds } });
    const ticketMap = {};
    tickets.forEach(t => {
      ticketMap[t.registration.toString()] = t;
    });

    const attendeeList = registrations.map(reg => {
      const ticket = ticketMap[reg._id.toString()];
      return {
        _id: reg._id,
        student: reg.student,
        status: reg.status,
        registeredAt: reg.registeredAt,
        ticketId: ticket ? ticket.ticketId : 'N/A',
        isCheckedIn: ticket ? ticket.isCheckedIn : false,
        checkedInAt: ticket ? ticket.checkedInAt : null
      };
    });

    return res.status(200).json({
      success: true,
      event: {
        _id: event._id,
        title: event.title,
        seatLimit: event.seatLimit,
        registeredCount: event.registeredCount
      },
      attendees: attendeeList
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * POST /api/events/checkin
 * Venue check-in counter: scan or enter ticketId
 */
router.post('/checkin', authenticateToken, authorizeRoles('organizer', 'admin'), requireApprovedOrganizer, async (req, res, next) => {
  try {
    const { ticketId } = req.body;
    if (!ticketId || !String(ticketId).trim()) {
      return res.status(400).json({
        success: false,
        message: 'Please provide a valid ticket code'
      });
    }

    const normalizedCode = String(ticketId).trim().toUpperCase();
    const ticket = await Ticket.findOne({ ticketId: normalizedCode })
      .populate({
        path: 'registration',
        populate: [
          { path: 'student', select: 'name email department phone' },
          { path: 'event', select: 'title venue eventDate organizer' }
        ]
      });

    if (!ticket || !ticket.registration || !ticket.registration.event) {
      return res.status(404).json({
        success: false,
        message: `Ticket "${normalizedCode}" was not found in the system.`
      });
    }

    const { event, student } = ticket.registration;

    // Check organizer authority for this event
    if (req.user.role === 'organizer' && event.organizer.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        message: `This ticket belongs to "${event.title}", which is managed by a different organizer.`
      });
    }

    if (ticket.registration.status === 'CANCELLED') {
      return res.status(400).json({
        success: false,
        message: 'This registration was cancelled. Entry cannot be permitted.'
      });
    }

    if (ticket.isCheckedIn) {
      const checkInTime = ticket.checkedInAt ? new Date(ticket.checkedInAt).toLocaleTimeString() : 'Earlier';
      return res.status(400).json({
        success: false,
        message: `Duplicate check-in warning! Ticket ${ticket.ticketId} was already scanned at ${checkInTime}.`,
        ticket,
        student,
        event
      });
    }

    ticket.isCheckedIn = true;
    ticket.checkedInAt = new Date();
    await ticket.save();

    return res.status(200).json({
      success: true,
      message: `Verified! Welcome ${student.name} to ${event.title}.`,
      ticket,
      student,
      event
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * GET /api/events/admin/pending
 * Pending event proposals queue for Admin
 */
router.get('/admin/pending', authenticateToken, authorizeRoles('admin'), async (req, res, next) => {
  try {
    const events = await Event.find({ status: 'PENDING' })
      .populate('category', 'name')
      .populate('organizer', 'name email organizationName')
      .sort({ createdAt: 1 });

    return res.status(200).json({ success: true, events });
  } catch (error) {
    return next(error);
  }
});

/**
 * PATCH /api/events/:eventId/review
 * Admin reviews pending event (APPROVED or REJECTED)
 */
router.patch('/:eventId/review', authenticateToken, authorizeRoles('admin'), async (req, res, next) => {
  try {
    const { status, rejectionReason = '' } = req.body;
    if (!['APPROVED', 'REJECTED'].includes(status)) {
      return res.status(400).json({ success: false, message: 'Review status must be APPROVED or REJECTED' });
    }
    if (status === 'REJECTED' && !String(rejectionReason).trim()) {
      return res.status(400).json({ success: false, message: 'Please provide a reason when rejecting an event proposal' });
    }

    const event = await Event.findOneAndUpdate(
      { _id: req.params.eventId, status: 'PENDING' },
      { $set: { status, rejectionReason: status === 'REJECTED' ? String(rejectionReason).trim() : '' } },
      { new: true, runValidators: true }
    )
      .populate('category', 'name')
      .populate('organizer', 'name email');

    if (!event) {
      return res.status(404).json({ success: false, message: 'Pending event proposal not found' });
    }

    return res.status(200).json({
      success: true,
      message: `Event proposal has been ${status.toLowerCase()}`,
      event
    });
  } catch (error) {
    if (error.name === 'CastError') {
      return res.status(400).json({ success: false, message: 'Invalid event ID' });
    }
    return next(error);
  }
});

/**
 * GET /api/events/my-registrations
 * Student: View personal event registrations and tickets
 */
router.get('/my-registrations', authenticateToken, authorizeRoles('student'), async (req, res, next) => {
  try {
    const registrations = await Registration.find({ student: req.user._id })
      .populate({
        path: 'event',
        populate: [
          { path: 'category', select: 'name' },
          { path: 'organizer', select: 'name organizationName' }
        ]
      })
      .sort({ registeredAt: -1 });

    // Attach tickets to each registration
    const regIds = registrations.map(r => r._id);
    const tickets = await Ticket.find({ registration: { $in: regIds } });
    const ticketMap = {};
    tickets.forEach(t => {
      ticketMap[t.registration.toString()] = t;
    });

    const fullRegistrations = registrations.map(reg => ({
      _id: reg._id,
      event: reg.event,
      status: reg.status,
      registeredAt: reg.registeredAt,
      ticket: ticketMap[reg._id.toString()] || null
    }));

    return res.status(200).json({ success: true, registrations: fullRegistrations });
  } catch (error) {
    return next(error);
  }
});

/**
 * POST /api/events/:eventId/register
 * Student: Atomic registration with concurrency protection
 */
router.post('/:eventId/register', authenticateToken, authorizeRoles('student'), async (req, res, next) => {
  let registration;
  let seatReserved = false;
  try {
    // Check if already registered
    const alreadyRegistered = await Registration.findOne({
      event: req.params.eventId,
      student: req.user._id,
      status: 'REGISTERED'
    });

    if (alreadyRegistered) {
      return res.status(409).json({
        success: false,
        message: 'You are already registered for this event. Check your Student Dashboard or My Tickets.'
      });
    }

    // Atomic seat check and increment
    const event = await Event.findOneAndUpdate(
      {
        _id: req.params.eventId,
        status: 'APPROVED',
        eventDate: { $gt: new Date() },
        $expr: { $lt: ['$registeredCount', '$seatLimit'] }
      },
      { $inc: { registeredCount: 1 } },
      { new: true }
    );

    if (!event) {
      return res.status(400).json({
        success: false,
        message: 'Registration unavailable: Event is either fully booked, has already concluded, or is not approved.'
      });
    }
    seatReserved = true;

    // Create or renew registration
    registration = await Registration.findOneAndUpdate(
      { event: event._id, student: req.user._id },
      { $set: { status: 'REGISTERED', registeredAt: new Date() } },
      { upsert: true, new: true, runValidators: true }
    );

    // Generate unique alphanumeric ticket code
    const ticketId = `EVT-${Date.now().toString(36).toUpperCase()}-${crypto.randomBytes(3).toString('hex').toUpperCase()}`;
    const qrData = JSON.stringify({
      ticketId,
      eventId: event._id.toString(),
      studentId: req.user._id.toString(),
      eventTitle: event.title
    });
    const qrCodeDataUrl = await QRCode.toDataURL(qrData, { width: 300, margin: 2 });

    const ticket = await Ticket.findOneAndUpdate(
      { registration: registration._id },
      {
        $set: {
          ticketId,
          qrCodeDataUrl,
          isCheckedIn: false,
          checkedInAt: null
        }
      },
      { upsert: true, new: true }
    );

    return res.status(201).json({
      success: true,
      message: 'Registration successful! Your digital QR ticket pass has been issued.',
      registration,
      ticket
    });
  } catch (error) {
    if (seatReserved) {
      await Event.updateOne({ _id: req.params.eventId, registeredCount: { $gt: 0 } }, { $inc: { registeredCount: -1 } });
    }
    if (error.code === 11000) {
      return res.status(409).json({ success: false, message: 'You are already registered for this event' });
    }
    return next(error);
  }
});

/**
 * POST /api/events/registrations/:registrationId/cancel
 * Student: Cancel an existing registration and release the reserved seat
 */
router.post('/registrations/:registrationId/cancel', authenticateToken, authorizeRoles('student'), async (req, res, next) => {
  try {
    const registration = await Registration.findOne({
      _id: req.params.registrationId,
      student: req.user._id,
      status: 'REGISTERED'
    });

    if (!registration) {
      return res.status(404).json({
        success: false,
        message: 'Active registration record not found'
      });
    }

    registration.status = 'CANCELLED';
    await registration.save();

    // Release seat atomically
    await Event.updateOne(
      { _id: registration.event, registeredCount: { $gt: 0 } },
      { $inc: { registeredCount: -1 } }
    );

    return res.status(200).json({
      success: true,
      message: 'Registration cancelled successfully. Your seat has been released.'
    });
  } catch (error) {
    return next(error);
  }
});

module.exports = router;
