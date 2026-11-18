const express = require('express');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const Department = require('../models/Department');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

const JWT_SECRET = process.env.JWT_SECRET || 'campus_event_super_secret_jwt_key_2026';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '24h';

function createToken(userId) {
  return jwt.sign({ id: userId }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
}

function publicUser(user) {
  const json = user.toJSON ? user.toJSON() : { ...user };
  delete json.password;
  return json;
}

/**
 * Public Registration Endpoint
 * Accessible only for Students and Organizers.
 * Public admin registration is strictly disallowed.
 */
router.post('/register', async (req, res, next) => {
  try {
    const { name, email, password, role, department, organizationName, phone } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Name, email, and password are required'
      });
    }

    if (String(password).length < 6) {
      return res.status(400).json({
        success: false,
        message: 'Password must be at least 6 characters'
      });
    }

    // Explicitly disallow self-registering as admin
    if (role === 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Administrator registration is restricted. Admin accounts are managed by system administrators.'
      });
    }

    const assignedRole = role === 'organizer' ? 'organizer' : 'student';

    const normalizedEmail = String(email).trim().toLowerCase();
    const existingUser = await User.findOne({ email: normalizedEmail });
    if (existingUser) {
      return res.status(409).json({
        success: false,
        message: 'An account with this email already exists'
      });
    }

    // Organizers start in PENDING status, students in APPROVED status
    const approvalStatus = assignedRole === 'organizer' ? 'PENDING' : 'APPROVED';

    const user = await User.create({
      name: String(name).trim(),
      email: normalizedEmail,
      password,
      role: assignedRole,
      department: department || null,
      organizationName: organizationName ? String(organizationName).trim() : '',
      phone: phone ? String(phone).trim() : '',
      approvalStatus,
      isActive: true
    });

    const populatedUser = await User.findById(user._id).populate('department', 'name');
    const token = createToken(user._id);

    const welcomeMessage = assignedRole === 'organizer'
      ? 'Organizer account registered. Your account is pending administrator approval before you can publish events.'
      : 'Student account registered successfully! Welcome to the campus event portal.';

    return res.status(201).json({
      success: true,
      message: welcomeMessage,
      token,
      user: publicUser(populatedUser)
    });
  } catch (error) {
    if (error.name === 'ValidationError') {
      const message = Object.values(error.errors)[0]?.message || 'Invalid registration details';
      return res.status(400).json({ success: false, message });
    }
    if (error.code === 11000) {
      return res.status(409).json({ success: false, message: 'An account with this email already exists' });
    }
    return next(error);
  }
});

/**
 * Universal Role-Based Login Endpoint
 * Supports Student, Organizer, and Admin authentication.
 * Optional `expectedRole` parameter validates intended login role tab.
 */
router.post('/login', async (req, res, next) => {
  try {
    const { email, password, expectedRole } = req.body;
    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Email and password are required'
      });
    }

    const user = await User.findOne({ email: String(email).trim().toLowerCase() }).populate('department', 'name');
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }

    if (!user.isActive) {
      return res.status(403).json({
        success: false,
        message: 'This account has been deactivated. Please contact campus administration.'
      });
    }

    const passwordMatches = await user.comparePassword(password);
    if (!passwordMatches) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }

    // If login was initiated from a role-specific tab, provide clear feedback
    if (expectedRole && user.role !== expectedRole) {
      const roleLabel = user.role.charAt(0).toUpperCase() + user.role.slice(1);
      const expectedLabel = expectedRole.charAt(0).toUpperCase() + expectedRole.slice(1);
      return res.status(403).json({
        success: false,
        message: `Role mismatch: This account is registered as a ${roleLabel}. Please use the ${roleLabel} Login option instead of ${expectedLabel} Login.`,
        detectedRole: user.role
      });
    }

    const token = createToken(user._id);
    return res.status(200).json({
      success: true,
      message: `Welcome back, ${user.name}!`,
      token,
      user: publicUser(user)
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * Get Current Authenticated User Session
 */
router.get('/me', authenticateToken, async (req, res, next) => {
  try {
    const user = await User.findById(req.user._id).populate('department', 'name');
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    return res.status(200).json({
      success: true,
      user: publicUser(user)
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * Update Current User Profile
 */
router.put('/profile', authenticateToken, async (req, res, next) => {
  try {
    const { name, phone, organizationName, department } = req.body;
    const updates = {};
    if (name) updates.name = String(name).trim();
    if (phone !== undefined) updates.phone = String(phone).trim();
    if (organizationName !== undefined) updates.organizationName = String(organizationName).trim();
    if (department !== undefined) updates.department = department || null;

    const user = await User.findByIdAndUpdate(
      req.user._id,
      { $set: updates },
      { new: true, runValidators: true }
    ).populate('department', 'name');

    return res.status(200).json({
      success: true,
      message: 'Profile updated successfully',
      user: publicUser(user)
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * Public Departments Directory Endpoint
 * Used to populate department dropdown menus.
 */
router.get('/departments', async (req, res, next) => {
  try {
    const departments = await Department.find().sort({ name: 1 });
    return res.status(200).json({
      success: true,
      departments
    });
  } catch (error) {
    return next(error);
  }
});

module.exports = router;
