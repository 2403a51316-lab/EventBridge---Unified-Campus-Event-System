require('dotenv').config();
const mongoose = require('mongoose');
const connectDB = require('../config/db');
const User = require('../models/User');
const Department = require('../models/Department');
const Category = require('../models/Category');
const Event = require('../models/Event');
const Registration = require('../models/Registration');
const Ticket = require('../models/Ticket');
const QRCode = require('qrcode');

async function seed() {
  const adminEmail = (process.env.ADMIN_EMAIL || 'admin@campus.com').trim().toLowerCase();
  const adminPassword = process.env.ADMIN_PASSWORD || 'Admin@123';
  const adminName = process.env.ADMIN_NAME || 'Campus Administrator';

  console.log('--- Starting Smart Campus Database Seeding ---');
  await connectDB();

  // 1. Seed Departments
  const departmentNames = [
    'Computer Science & Engineering',
    'Information Technology',
    'Electronics & Communication',
    'Mechanical Engineering',
    'School of Management'
  ];
  for (const name of departmentNames) {
    await Department.findOneAndUpdate(
      { name },
      { $setOnInsert: { name } },
      { upsert: true, new: true }
    );
  }
  console.log('✓ Departments seeded');
  const cseDept = await Department.findOne({ name: 'Computer Science & Engineering' });

  // 2. Seed Categories
  const categoryNames = ['Technology', 'Culture', 'Sports', 'Workshop', 'Seminar'];
  for (const name of categoryNames) {
    await Category.findOneAndUpdate(
      { name },
      { $setOnInsert: { name } },
      { upsert: true, new: true }
    );
  }
  console.log('✓ Categories seeded');
  const techCat = await Category.findOne({ name: 'Technology' });
  const cultCat = await Category.findOne({ name: 'Culture' });
  const workCat = await Category.findOne({ name: 'Workshop' });

  // 3. Seed Admin User (Idempotent)
  let admin = await User.findOne({ email: adminEmail });
  if (!admin) {
    admin = await User.create({
      name: adminName,
      email: adminEmail,
      password: adminPassword,
      role: 'admin',
      approvalStatus: 'APPROVED',
      isActive: true,
      department: cseDept?._id || null
    });
    console.log(`✓ Created Admin Account: ${adminEmail} (password: ${adminPassword})`);
  } else {
    admin.role = 'admin';
    admin.approvalStatus = 'APPROVED';
    admin.isActive = true;
    if (adminPassword) {
      admin.password = adminPassword;
    }
    await admin.save();
    console.log(`✓ Verified existing Admin Account: ${adminEmail}`);
  }

  // 4. Seed an APPROVED Sample Organizer
  let approvedOrg = await User.findOne({ email: 'codingclub@campus.com' });
  if (!approvedOrg) {
    approvedOrg = await User.create({
      name: 'Campus Coding Club',
      email: 'codingclub@campus.com',
      password: 'Organizer@123',
      role: 'organizer',
      organizationName: 'Coding & Algorithmic Society',
      approvalStatus: 'APPROVED',
      isActive: true,
      department: cseDept?._id || null
    });
    console.log('✓ Created Approved Organizer: codingclub@campus.com (Organizer@123)');
  }

  // 5. Seed a PENDING Sample Organizer (Ready for Admin Approval testing)
  let pendingOrg = await User.findOne({ email: 'robotics@campus.com' });
  if (!pendingOrg) {
    pendingOrg = await User.create({
      name: 'Robotics & AI Guild',
      email: 'robotics@campus.com',
      password: 'Organizer@123',
      role: 'organizer',
      organizationName: 'Department Robotics Guild',
      approvalStatus: 'PENDING',
      isActive: true,
      department: cseDept?._id || null
    });
    console.log('✓ Created Pending Organizer (for Admin test): robotics@campus.com (Organizer@123)');
  }

  // 6. Seed a Sample Student
  let student = await User.findOne({ email: 'alex.student@campus.com' });
  if (!student) {
    student = await User.create({
      name: 'Alex Johnson',
      email: 'alex.student@campus.com',
      password: 'Student@123',
      role: 'student',
      approvalStatus: 'APPROVED',
      isActive: true,
      department: cseDept?._id || null
    });
    console.log('✓ Created Student Account: alex.student@campus.com (Student@123)');
  }

  // 7. Seed Sample Events
  const futureDate1 = new Date();
  futureDate1.setDate(futureDate1.getDate() + 7);
  futureDate1.setHours(10, 0, 0, 0);

  const futureDate2 = new Date();
  futureDate2.setDate(futureDate2.getDate() + 14);
  futureDate2.setHours(14, 30, 0, 0);

  let hackathon = await Event.findOne({ title: 'Annual Campus Hackathon 2026' });
  if (!hackathon) {
    hackathon = await Event.create({
      organizer: approvedOrg._id,
      category: techCat?._id,
      title: 'Annual Campus Hackathon 2026',
      description: 'A 24-hour university-wide hackathon challenging developers and designers to build solutions for sustainability and campus life.',
      venue: 'Main Auditorium & Innovation Lab',
      eventDate: futureDate1,
      seatLimit: 120,
      registeredCount: 1,
      status: 'APPROVED'
    });
    console.log('✓ Created Approved Event: Annual Campus Hackathon 2026');

    // Create registration and QR ticket for student
    const reg = await Registration.create({
      event: hackathon._id,
      student: student._id,
      status: 'REGISTERED'
    });

    const ticketId = 'EVT-HACK26-ALEX1';
    const qrData = JSON.stringify({
      ticketId,
      eventId: hackathon._id.toString(),
      studentId: student._id.toString(),
      eventTitle: hackathon.title
    });
    const qrCodeDataUrl = await QRCode.toDataURL(qrData, { width: 300, margin: 2 });

    await Ticket.create({
      registration: reg._id,
      ticketId,
      qrCodeDataUrl,
      isCheckedIn: false
    });
    console.log('✓ Issued Ticket & QR Code pass for sample student');
  }

  let aiWorkshop = await Event.findOne({ title: 'Hands-on Generative AI Workshop' });
  if (!aiWorkshop) {
    await Event.create({
      organizer: approvedOrg._id,
      category: workCat?._id,
      title: 'Hands-on Generative AI Workshop',
      description: 'Learn modern LLM application development, prompting engineering, and vector databases.',
      venue: 'Computer Center Lab 3',
      eventDate: futureDate2,
      seatLimit: 60,
      registeredCount: 0,
      status: 'PENDING'
    });
    console.log('✓ Created Pending Event Proposal (for Admin test): Hands-on Generative AI Workshop');
  }

  console.log('=======================================================');
  console.log('🎉 Seeding Complete!');
  console.log('🔑 Credentials Summary:');
  console.log(`   [Admin]     ${adminEmail} / ${adminPassword}`);
  console.log(`   [Organizer] codingclub@campus.com / Organizer@123 (Approved)`);
  console.log(`   [Organizer] robotics@campus.com   / Organizer@123 (Pending approval)`);
  console.log(`   [Student]   alex.student@campus.com / Student@123`);
  console.log('=======================================================');
}

seed()
  .catch(err => {
    console.error('[Seed Error]:', err);
    process.exitCode = 1;
  })
  .finally(async () => {
    await mongoose.disconnect();
  });
