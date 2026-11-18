const express = require('express');
const User = require('../models/User');
const Event = require('../models/Event');
const Registration = require('../models/Registration');
const Department = require('../models/Department');
const Category = require('../models/Category');
const { authenticateToken, authorizeRoles } = require('../middleware/auth');

const router = express.Router();

// All routes in this file require valid JWT and Admin role
router.use(authenticateToken, authorizeRoles('admin'));

/**
 * GET /api/admin/stats
 * Aggregated statistics for the Admin Dashboard
 */
router.get('/stats', async (req, res, next) => {
  try {
    const [
      totalStudents,
      totalOrganizers,
      pendingApprovals,
      approvedOrganizers,
      rejectedOrganizers,
      totalEvents,
      pendingEvents,
      approvedEvents,
      rejectedEvents,
      totalRegistrations
    ] = await Promise.all([
      User.countDocuments({ role: 'student' }),
      User.countDocuments({ role: 'organizer' }),
      User.countDocuments({ role: 'organizer', approvalStatus: 'PENDING' }),
      User.countDocuments({ role: 'organizer', approvalStatus: 'APPROVED' }),
      User.countDocuments({ role: 'organizer', approvalStatus: 'REJECTED' }),
      Event.countDocuments(),
      Event.countDocuments({ status: 'PENDING' }),
      Event.countDocuments({ status: 'APPROVED' }),
      Event.countDocuments({ status: 'REJECTED' }),
      Registration.countDocuments({ status: 'REGISTERED' })
    ]);

    return res.status(200).json({
      success: true,
      stats: {
        totalStudents,
        totalOrganizers,
        pendingApprovals,
        approvedOrganizers,
        rejectedOrganizers,
        totalEvents,
        pendingEvents,
        approvedEvents,
        rejectedEvents,
        totalRegistrations
      }
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * GET /api/admin/pending-organizers
 * Retrieve all organizer accounts waiting for approval
 */
router.get('/pending-organizers', async (req, res, next) => {
  try {
    const pendingOrganizers = await User.find({
      role: 'organizer',
      approvalStatus: 'PENDING'
    })
      .populate('department', 'name')
      .sort({ createdAt: -1 });

    return res.status(200).json({
      success: true,
      organizers: pendingOrganizers
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * PATCH /api/admin/organizers/:userId/approval
 * Approve or reject an organizer account
 */
router.patch('/organizers/:userId/approval', async (req, res, next) => {
  try {
    const { status, rejectionReason } = req.body;

    if (!['APPROVED', 'REJECTED'].includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'Status must be either APPROVED or REJECTED'
      });
    }

    if (status === 'REJECTED' && !String(rejectionReason || '').trim()) {
      return res.status(400).json({
        success: false,
        message: 'A rejection reason is required when rejecting an organizer account'
      });
    }

    const organizer = await User.findOne({
      _id: req.params.userId,
      role: 'organizer'
    });

    if (!organizer) {
      return res.status(404).json({
        success: false,
        message: 'Organizer account not found'
      });
    }

    organizer.approvalStatus = status;
    organizer.rejectionReason = status === 'REJECTED' ? String(rejectionReason).trim() : '';
    await organizer.save();

    const populated = await User.findById(organizer._id).populate('department', 'name');

    return res.status(200).json({
      success: true,
      message: `Organizer account has been ${status.toLowerCase()} successfully`,
      organizer: populated
    });
  } catch (error) {
    if (error.name === 'CastError') {
      return res.status(400).json({ success: false, message: 'Invalid organizer ID' });
    }
    return next(error);
  }
});

/**
 * GET /api/admin/users
 * Filter and search all registered users (students, organizers, admins)
 */
router.get('/users', async (req, res, next) => {
  try {
    const { role, approvalStatus, search } = req.query;
    const filter = {};

    if (role && ['student', 'organizer', 'admin'].includes(role)) {
      filter.role = role;
    }
    if (approvalStatus && ['PENDING', 'APPROVED', 'REJECTED'].includes(approvalStatus)) {
      filter.approvalStatus = approvalStatus;
    }
    if (search) {
      const regex = new RegExp(search.trim(), 'i');
      filter.$or = [
        { name: regex },
        { email: regex },
        { organizationName: regex }
      ];
    }

    const users = await User.find(filter)
      .populate('department', 'name')
      .sort({ createdAt: -1 });

    return res.status(200).json({
      success: true,
      users
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * PATCH /api/admin/users/:userId/toggle-status
 * Activate or deactivate a user account
 */
router.patch('/users/:userId/toggle-status', async (req, res, next) => {
  try {
    const user = await User.findById(req.params.userId);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }

    // Prevent deactivating own admin account
    if (user._id.toString() === req.user._id.toString()) {
      return res.status(400).json({ success: false, message: 'You cannot deactivate your own admin account' });
    }

    user.isActive = !user.isActive;
    await user.save();

    return res.status(200).json({
      success: true,
      message: `User account is now ${user.isActive ? 'active' : 'suspended'}`,
      user
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * GET /api/admin/events
 * Retrieve all events across all statuses
 */
router.get('/events', async (req, res, next) => {
  try {
    const { status, category } = req.query;
    const filter = {};

    if (status && ['PENDING', 'APPROVED', 'REJECTED', 'CANCELLED'].includes(status)) {
      filter.status = status;
    }
    if (category) {
      filter.category = category;
    }

    const events = await Event.find(filter)
      .populate('category', 'name')
      .populate('organizer', 'name email organizationName')
      .sort({ createdAt: -1 });

    return res.status(200).json({
      success: true,
      events
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * POST /api/admin/departments
 * Create new department
 */
router.post('/departments', async (req, res, next) => {
  try {
    const { name } = req.body;
    if (!name || !String(name).trim()) {
      return res.status(400).json({ success: false, message: 'Department name is required' });
    }
    const dept = await Department.create({ name: String(name).trim() });
    return res.status(201).json({ success: true, department: dept });
  } catch (error) {
    if (error.code === 11000) {
      return res.status(409).json({ success: false, message: 'Department already exists' });
    }
    return next(error);
  }
});

module.exports = router;
