const jwt = require('jsonwebtoken');
const User = require('../models/User');

/**
 * Middleware: authenticateToken
 * Verifies the JWT Bearer token sent in the Authorization header.
 * Attaches the authenticated user object to req.user.
 */
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'] || req.headers['Authorization'];
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        message: 'Access denied: No authentication token provided'
      });
    }

    const token = authHeader.split(' ')[1];
    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access denied: Malformed authorization header'
      });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'campus_event_super_secret_jwt_key_2026');

    // Retrieve active user from database to ensure account wasn't deactivated/deleted
    const user = await User.findById(decoded.id).select('-password');
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication failed: User no longer exists'
      });
    }

    if (!user.isActive) {
      return res.status(403).json({
        success: false,
        message: 'Account suspended: Please contact your campus administrator'
      });
    }

    // Attach user to request object
    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Session expired: Please log in again'
      });
    }
    return res.status(401).json({
      success: false,
      message: 'Invalid or forged authentication token'
    });
  }
};

/**
 * Middleware Factory: authorizeRoles
 * Enforces Role-Based Access Control (RBAC).
 * Allows only users whose role matches one of the specified allowed roles.
 * 
 * Usage:
 *   router.post('/events', authenticateToken, authorizeRoles('admin', 'organizer'), handler);
 */
const authorizeRoles = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: `Forbidden: Access requires one of [${roles.join(', ')}] roles. Your role is '${req.user.role}'.`
      });
    }

    next();
  };
};

/**
 * Middleware: requireApprovedOrganizer
 * Ensures an organizer has been approved by the Admin before accessing restricted
 * features such as event creation, event updates, and venue check-in.
 */
const requireApprovedOrganizer = (req, res, next) => {
  if (!req.user) {
    return res.status(401).json({ success: false, message: 'Authentication required' });
  }

  // Admins always have access
  if (req.user.role === 'admin') {
    return next();
  }

  if (req.user.role !== 'organizer') {
    return res.status(403).json({
      success: false,
      message: 'Forbidden: Organizer privileges required'
    });
  }

  if (req.user.approvalStatus !== 'APPROVED') {
    const reasonText = req.user.rejectionReason ? ` Reason: ${req.user.rejectionReason}` : '';
    const message = req.user.approvalStatus === 'PENDING'
      ? 'Your organizer account is pending administrator approval. Please wait for an administrator to approve your account.'
      : `Your organizer account registration was rejected.${reasonText}`;

    return res.status(403).json({
      success: false,
      message,
      approvalStatus: req.user.approvalStatus
    });
  }

  next();
};

module.exports = {
  authenticateToken,
  authorizeRoles,
  requireApprovedOrganizer
};
