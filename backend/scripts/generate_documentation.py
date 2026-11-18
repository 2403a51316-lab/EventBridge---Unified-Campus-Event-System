import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw consistent
    academic running headers, rules, and page numbers matching the sample report.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        # Page 1 is the cover/title page - no headers or page numbers
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))

        # Thin running top header rule
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.75)
        self.line(54, 742, 558, 742)

        # Page number at bottom right (matches sample pages 2-26)
        self.drawRightString(558, 38, str(self._pageNumber))

        self.restoreState()


def create_diagram_frame(title, caption, height=420, width=504):
    """Generates an aesthetic dashed-border placeholder box for diagrams and screenshots."""
    d = Drawing(width, height)
    # Background rectangle with rounded corners and dashed border
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#f8fafc"), strokeColor=colors.HexColor("#94a3b8"), strokeWidth=1, strokeDashArray=[4, 4], rx=6, ry=6))
    # Title label
    d.add(String(width / 2, height / 2 + 12, f"[{title}]", textAnchor='middle', fontName='Helvetica-Bold', fontSize=11, fillColor=colors.HexColor("#1e3a8a")))
    d.add(String(width / 2, height / 2 - 8, "(Space reserved for diagram / visual capture — Insert image here)", textAnchor='middle', fontName='Helvetica-Oblique', fontSize=9, fillColor=colors.HexColor("#64748b")))
    
    caption_p = Paragraph(f"<i>{caption}</i>", ParagraphStyle(
        'CaptionStyle',
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#475569")
    ))
    return [Spacer(1, 10), d, Spacer(1, 8), caption_p]


def build_pdf(filename="Smart_Campus_Documentation.pdf"):
    # Page dimensions: letter is 612 x 792 pt. 54pt margins leave 504pt printable width and 684pt height.
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Typography hierarchy
    cover_title = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=21,
        alignment=1,
        textColor=colors.HexColor("#0f172a")
    )
    
    cover_sub = ParagraphStyle(
        'CoverSub',
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#334155")
    )

    h1_style = ParagraphStyle(
        'H1_Section',
        fontName='Helvetica-Bold',
        fontSize=13.5,
        leading=18,
        spaceBefore=8,
        spaceAfter=12,
        alignment=1,
        textColor=colors.HexColor("#1e3a8a")
    )

    h2_style = ParagraphStyle(
        'H2_Sub',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#0f172a")
    )

    h3_style = ParagraphStyle(
        'H3_Minor',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        spaceBefore=7,
        spaceAfter=4,
        textColor=colors.HexColor("#1e3a8a")
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        spaceAfter=7,
        alignment=4, # Justified
        textColor=colors.HexColor("#1e293b")
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
        textColor=colors.HexColor("#1e293b")
    )

    th_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1e293b")
    )

    td_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    code_block = ParagraphStyle(
        'CodeBlock',
        fontName='Courier',
        fontSize=8,
        leading=11.5,
        leftIndent=12,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE PAGE
    # =========================================================================
    story.append(Spacer(1, 45))
    story.append(Paragraph("<b>“Smart Campus Event Management System — Web-Based College Activity, Approval Workflow, and QR Entry Platform”</b>", cover_title))
    story.append(Spacer(1, 14))
    story.append(Paragraph("A Course Project Report<br/>Submitted in the partial fulfillment of the completion of the course", cover_sub))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>SOFTWARE ENGINEERING AND SYSTEM DESIGN</b><br/><b>(24CS301PC311)</b>", ParagraphStyle('CourseCode', parent=cover_sub, fontName='Helvetica-Bold', fontSize=12, leading=16)))
    story.append(Spacer(1, 14))
    story.append(Paragraph("In III Year, I Semester B. Tech-CSE", cover_sub))
    story.append(Spacer(1, 28))
    
    story.append(Paragraph("Submitted by", cover_sub))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Lunghimpou kamei</b>", ParagraphStyle('SName', parent=cover_sub, fontName='Helvetica-Bold', fontSize=12)))
    story.append(Paragraph("<b>2503A51L16</b>", ParagraphStyle('SRoll', parent=cover_sub, fontName='Helvetica-Bold', fontSize=11)))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Under the supervision of the faculty", cover_sub))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Dr. Shanker Chandre</b><br/>Associate Professor,<br/>School Of Computer Science & Artificial Intelligence", cover_sub))
    story.append(Spacer(1, 8))
    story.append(Paragraph("2026-2027", cover_sub))
    story.append(Spacer(1, 26))

    # University Logo
    story.append(Paragraph("<font size='36' color='#1d4ed8'><b>sru</b></font>", ParagraphStyle('SRULogo', alignment=1, spaceAfter=14)))
    story.append(Paragraph("Department of Computer Science & Artificial Intelligence<br/><b>SR University</b><br/>Warangal, Telangana, India", cover_sub))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: INDEX
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>INDEX</b>", h1_style))
    story.append(Spacer(1, 14))

    index_rows = [
        [Paragraph("<b>1. Abstract</b>", td_bold), Paragraph("<b>3</b>", td_style)],
        [Paragraph("<b>2. Introduction</b>", td_bold), Paragraph("<b>4</b>", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.1 Problem Statement", td_style), Paragraph("4", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.2 Objectives", td_style), Paragraph("4", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.3 Scope", td_style), Paragraph("4", td_style)],
        [Paragraph("<b>3. Software Requirements Specification (SRS)</b>", td_bold), Paragraph("<b>5</b>", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.1 Functional Requirements", td_style), Paragraph("5", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.2 Non-Functional Requirements", td_style), Paragraph("6", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.3 Hardware and Software Requirements", td_style), Paragraph("6", td_style)],
        [Paragraph("<b>4. System Analysis</b>", td_bold), Paragraph("<b>8</b>", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.1 Existing System", td_style), Paragraph("8", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.2 Proposed System", td_style), Paragraph("8", td_style)],
        [Paragraph("<b>5. System Design</b>", td_bold), Paragraph("<b>9</b>", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.1 System Architecture", td_style), Paragraph("9", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.2 Use Case Diagram", td_style), Paragraph("11", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.3 Class Diagram", td_style), Paragraph("12", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.4 Sequence Diagram", td_style), Paragraph("13", td_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.5 Activity Diagram", td_style), Paragraph("14", td_style)],
        [Paragraph("<b>6. Methodology</b>", td_bold), Paragraph("<b>16</b>", td_style)],
        [Paragraph("<b>7. Implementation</b>", td_bold), Paragraph("<b>19</b>", td_style)],
        [Paragraph("<b>8. Output Screenshots</b>", td_bold), Paragraph("<b>22</b>", td_style)],
        [Paragraph("<b>9. Conclusion</b>", td_bold), Paragraph("<b>25</b>", td_style)],
        [Paragraph("<b>10. References</b>", td_bold), Paragraph("<b>26</b>", td_style)]
    ]
    t_idx = Table(index_rows, colWidths=[444, 60])
    t_idx.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
        ('ALIGN', (1,0), (1,-1), 'RIGHT')
    ]))
    story.append(t_idx)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: 1. ABSTRACT
    # =========================================================================
    story.append(Paragraph("<b>1. ABSTRACT</b>", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Smart Campus Event Management System</b> is a full-stack web application developed as a Software Engineering and System Design course project to govern collegiate activities, departmental symposiums, technical hackathons, and cultural fests. The platform connects three primary institutional actors—Students, Event Organizers (representing academic departments and registered student clubs), and Campus Administrators—under a unified, secure, and automated operational framework.",
        body_style
    ))
    story.append(Paragraph(
        "In traditional university environments, campus event management relies on informal message boards, paper circulars, and disconnected spreadsheets. This workflow frequently results in unsanctioned event scheduling, venue double-booking, uncontrolled seat allocation, and manual paper-based door checks prone to proxy attendance. The Smart Campus system resolves these challenges by introducing a rigorous multi-tier event lifecycle that enforces administrative vetting before events appear on the public catalog.",
        body_style
    ))
    story.append(Paragraph(
        "For event registration, the application incorporates a concurrency-controlled atomic reservation engine. Built upon MongoDB atomic operators with pre-condition queries, the system completely prevents overbooking even under high-volume concurrent booking spikes. Upon successful registration, the system dynamically generates a cryptographically unique digital ticket containing an encoded Quick Response (QR) code. Organizers verify attendee credentials at venue gates using a real-time web-based check-in desk that timestamps admissions and automatically detects duplicate scan attempts.",
        body_style
    ))
    story.append(Paragraph(
        "The application architecture leverages Node.js and Express for the RESTful API tier, MongoDB with Mongoose for persistent document storage, and JSON Web Tokens (JWT) with bcryptjs for secure role-based access control. The frontend is engineered with responsive HTML5, CSS3, modern vanilla JavaScript fetch APIs, and Bootstrap 5 CDN components without external framework bloat. Administrative and organizer dashboards deliver live aggregated metrics on registrations, seat capacity, attendance rates, and pending account approvals. The system demonstrates a robust, production-ready solution that enhances campus community engagement while maintaining institutional accountability.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: 2. INTRODUCTION
    # =========================================================================
    story.append(Paragraph("<b>2. INTRODUCTION</b>", h1_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Co-curricular and extra-curricular activities represent an integral component of university education. From competitive technical hackathons and coding symposiums to cultural galas and varsity athletics, events foster collaboration and innovation. However, coordinating these activities across disparate engineering departments and student societies presents complex logistical and operational challenges. A centralized, role-isolated event platform is required to streamline event proposal, administrative governance, student reservation, and physical door verification.",
        body_style
    ))
    story.append(Paragraph(
        "The Smart Campus Event Management System provides an integrated digital ecosystem. By enforcing a formal administrative approval workflow, providing atomic seat booking, and generating tamper-proof QR code admission passes, the platform ensures transparency, efficiency, and verifiable audit trails for all campus activities.",
        body_style
    ))

    story.append(Paragraph("<b>2.1 Problem Statement</b>", h2_style))
    story.append(Paragraph(
        "Conventional campus event handling is fragmented. Student organizers announce events through posters or social media without centralized approval, risking venue collisions and unauthorized resource utilization. Event registration through static forms lacks concurrency controls, resulting in seat overbooking and overcrowded auditoriums. Furthermore, attendance verification through paper rosters is slow, prone to fraudulent proxy sign-ins, and deprives organizers of real-time attendance analytics. The primary problem addressed is the absence of an integrated, automated software system providing verified account workflows, atomic capacity management, and fraud-resistant gate check-in.",
        body_style
    ))

    story.append(Paragraph("<b>2.2 Objectives</b>", h2_style))
    story.append(Paragraph("• To implement a multi-role authentication system with strict separation between Students, Organizers, and Admins.", bullet_style))
    story.append(Paragraph("• To construct a formal administrative workflow ensuring club events require dean or faculty approval prior to publication.", bullet_style))
    story.append(Paragraph("• To prevent venue overbooking through high-concurrency atomic seat reservation algorithms.", bullet_style))
    story.append(Paragraph("• To dynamically generate unique digital tickets with cryptographic QR codes upon confirmed registration.", bullet_style))
    story.append(Paragraph("• To provide organizers with a high-speed gate check-in scanner that detects and rejects duplicate passes.", bullet_style))
    story.append(Paragraph("• To provide interactive role-based dashboards delivering real-time statistics via MongoDB aggregation pipelines.", bullet_style))
    story.append(Paragraph("• To design a clean, responsive user interface supporting desktop, tablet, and mobile environments without template engines.", bullet_style))

    story.append(Paragraph("<b>2.3 Scope</b>", h2_style))
    story.append(Paragraph(
        "The project encompasses the entire event lifecycle within a collegiate institution. It supports self-registration for students and clubs, administrative vetting for organizer privileges, categorized event proposals, public catalog filtering, real-time ticket cancellation with automatic seat reclamation, and gate attendance tracking. The system is designed for deployment on local campus servers or cloud environments utilizing MongoDB Atlas and Node.js LTS.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: 3. SOFTWARE REQUIREMENTS SPECIFICATION (SRS) - 3.1
    # =========================================================================
    story.append(Paragraph("<b>3. SOFTWARE REQUIREMENTS SPECIFICATION (SRS)</b>", h1_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "This section defines the expected services of the Smart Campus platform and the quality constraints applied to the implementation. The primary actors are <b>Students</b>, <b>Event Organizers</b>, and <b>Campus Administrators</b>.",
        body_style
    ))
    story.append(Paragraph("<b>3.1 Functional Requirements</b>", h2_style))

    fr_rows = [
        [Paragraph("<b>ID</b>", th_style), Paragraph("<b>Requirement</b>", th_style), Paragraph("<b>Description</b>", th_style)],
        [Paragraph("FR-01", td_bold), Paragraph("Role-Based Registration", td_bold), Paragraph("The system shall permit self-registration for Students and Organizers while disallowing public Admin registration.", td_style)],
        [Paragraph("FR-02", td_bold), Paragraph("JWT Authentication", td_bold), Paragraph("The system shall authenticate credentials using bcrypt hashing and issue signed JSON Web Tokens (24h validity).", td_style)],
        [Paragraph("FR-03", td_bold), Paragraph("Organizer Vetting", td_bold), Paragraph("New organizer accounts shall enter PENDING status and require Admin approval before event creation privileges unlock.", td_style)],
        [Paragraph("FR-04", td_bold), Paragraph("Event Proposal", td_bold), Paragraph("Approved organizers shall submit event proposals specifying title, category, date, venue, seat limit, and agenda.", td_style)],
        [Paragraph("FR-05", td_bold), Paragraph("Admin Event Moderation", td_bold), Paragraph("Administrators shall review pending proposals and assign APPROVED or REJECTED status with mandatory rejection feedback.", td_style)],
        [Paragraph("FR-06", td_bold), Paragraph("Public Event Catalog", td_bold), Paragraph("The system shall display approved upcoming events with dynamic category filtering and keyword search.", td_style)],
        [Paragraph("FR-07", td_bold), Paragraph("Atomic Seat Reservation", td_bold), Paragraph("The system shall execute atomic conditional seat decrements to strictly eliminate overbooking under concurrency.", td_style)],
        [Paragraph("FR-08", td_bold), Paragraph("QR Ticket Issuance", td_bold), Paragraph("Upon confirmed registration, the system shall issue a unique alphanumeric ticket code and Base64 QR code pass.", td_style)],
        [Paragraph("FR-09", td_bold), Paragraph("Duplicate Booking Block", td_bold), Paragraph("The system shall enforce a unique compound index on (event, student) preventing multiple passes per student.", td_style)],
        [Paragraph("FR-10", td_bold), Paragraph("Pass Cancellation", td_bold), Paragraph("Students shall be able to cancel active reservations, automatically incrementing remaining venue capacity.", td_style)],
        [Paragraph("FR-11", td_bold), Paragraph("Venue Gate Check-In", td_bold), Paragraph("Organizers shall verify attendee tickets by code/scan, recording check-in timestamps in the database.", td_style)],
        [Paragraph("FR-12", td_bold), Paragraph("Duplicate Scan Warning", td_bold), Paragraph("The gate scanner shall reject already checked-in passes and display previous entry timestamps.", td_style)],
        [Paragraph("FR-13", td_bold), Paragraph("Admin Analytics", td_bold), Paragraph("The system shall compute aggregated campus counts: total students, active organizers, pending approvals, and bookings.", td_style)],
        [Paragraph("FR-14", td_bold), Paragraph("Account Governance", td_bold), Paragraph("Administrators shall be able to suspend or activate student and organizer accounts with immediate effect.", td_style)]
    ]
    t_fr = Table(fr_rows, colWidths=[44, 126, 334])
    t_fr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_fr)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: 3.2 NON-FUNCTIONAL REQUIREMENTS & 3.3 HARDWARE
    # =========================================================================
    story.append(Paragraph("<b>3.2 Non-Functional Requirements</b>", h2_style))
    
    nfr_rows = [
        [Paragraph("<b>Quality Attribute</b>", th_style), Paragraph("<b>Requirement Specification</b>", th_style)],
        [Paragraph("Usability", td_bold), Paragraph("Interfaces feature intuitive Bootstrap 5 layouts, responsive navigation bars, and clear status badges requiring no prior user training.", td_style)],
        [Paragraph("Security & RBAC", td_bold), Paragraph("Endpoints validate cryptographic JWTs and enforce role-based access. Passwords are encrypted with bcrypt (salt factor 10).", td_style)],
        [Paragraph("Concurrency & Integrity", td_bold), Paragraph("Seat allocation uses atomic MongoDB findOneAndUpdate operations to guarantee zero overbooking during registration rushes.", td_style)],
        [Paragraph("Performance & Latency", td_bold), Paragraph("API response times remain under 120ms under typical campus workloads through indexed queries on event dates and statuses.", td_style)],
        [Paragraph("Reliability & Resilience", td_bold), Paragraph("Graceful exception handling returns standardized JSON error payloads { success: false, message } with appropriate HTTP status codes.", td_style)],
        [Paragraph("Maintainability", td_bold), Paragraph("Strict Model-Controller-Route separation on the backend and modular JavaScript helpers (api.js, auth.js) on the frontend.", td_style)],
        [Paragraph("Traceability", td_bold), Paragraph("Timestamps are logged for event creation, registration submission, and venue check-in scans for complete audit trails.", td_style)],
        [Paragraph("Device Responsiveness", td_bold), Paragraph("Web layouts dynamically adapt across desktop monitors, tablets, and organizer mobile screens for venue check-ins.", td_style)]
    ]
    t_nfr = Table(nfr_rows, colWidths=[120, 384])
    t_nfr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_nfr)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>3.3 Hardware and Software Requirements</b>", h2_style))
    story.append(Paragraph("<b>Hardware Requirements</b>", h3_style))
    story.append(Paragraph("• Standard desktop computer or laptop capable of running Node.js runtime and web browser.", bullet_style))
    story.append(Paragraph("• Processor: Dual-core 2.0 GHz or higher (Intel Core i3/i5 or AMD Ryzen equivalent).", bullet_style))
    story.append(Paragraph("• Memory: Minimum 4 GB RAM recommended for comfortable local hosting and database services.", bullet_style))
    story.append(Paragraph("• Storage: At least 500 MB free disk space for node_modules, source code, and database records.", bullet_style))
    story.append(Paragraph("• Display: 1280x720 minimum resolution (responsive design adapts down to 360px mobile viewports).", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: 3.3 SOFTWARE REQUIREMENTS & DEPLOYMENT
    # =========================================================================
    story.append(Paragraph("<b>Software Requirements</b>", h3_style))
    sw_rows = [
        [Paragraph("<b>Component</b>", th_style), Paragraph("<b>Requirement / Purpose</b>", th_style)],
        [Paragraph("Operating System", td_bold), Paragraph("Windows 10/11, macOS, or Linux (cross-platform Node.js runtime environment).", td_style)],
        [Paragraph("Runtime Environment", td_bold), Paragraph("Node.js LTS (v18.x or v20.x recommended).", td_style)],
        [Paragraph("Backend Framework", td_bold), Paragraph("Express.js (v4.19+) for REST API routing and static frontend delivery.", td_style)],
        [Paragraph("Database Engine", td_bold), Paragraph("MongoDB v6.0+ (Local Community Edition or MongoDB Atlas cloud cluster).", td_style)],
        [Paragraph("Object Data Modeling", td_bold), Paragraph("Mongoose ODM (v8.5+) for schema validation, indexing, and population.", td_style)],
        [Paragraph("Security Libraries", td_bold), Paragraph("jsonwebtoken (v9.0+) for JWT session tokens; bcryptjs for credential hashing.", td_style)],
        [Paragraph("QR Code Engine", td_bold), Paragraph("qrcode npm package (v1.5+) for generating Base64 Data URI ticket QR codes.", td_style)],
        [Paragraph("Frontend Stack", td_bold), Paragraph("HTML5, CSS3, vanilla JavaScript (Fetch API), Bootstrap 5.3 CDN, Bootstrap Icons.", td_style)],
        [Paragraph("Development Tools", td_bold), Paragraph("Visual Studio Code, PowerShell / Bash terminal, Nodemon for live reloads.", td_style)]
    ]
    t_sw = Table(sw_rows, colWidths=[120, 384])
    t_sw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_sw)
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "The application does not require a separate build or transpilation step. The Express web server directly serves the static presentation layer from the <code>frontend/</code> directory and mounts the REST API controllers under <code>/api</code>. Database schema indexes are automatically constructed upon initial Mongoose connection.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: 4. SYSTEM ANALYSIS
    # =========================================================================
    story.append(Paragraph("<b>4. SYSTEM ANALYSIS</b>", h1_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>4.1 Existing System</b>", h2_style))
    story.append(Paragraph(
        "In a conventional university setup, event management relies on paper approval forms, static Google Forms, and manual paper rosters. Student clubs post announcements on social media or bulletin boards without formal institutional clearance. Approvals from department heads require physical signatures that often cause delays. At event venues, student volunteers tick off names on printed rosters, creating slow queues and enabling unverified attendees to enter via borrowed credentials.",
        body_style
    ))
    story.append(Paragraph("<b>Limitations of the Existing Approach:</b>", h3_style))
    story.append(Paragraph("• <b>Overbooking Disasters:</b> Static forms cannot enforce atomic seat caps in real time, causing overcrowded auditoriums and fire safety violations.", bullet_style))
    story.append(Paragraph("• <b>Forged Physical Passes:</b> Paper passes or confirmation emails can be easily forwarded, duplicated, or shared among students.", bullet_style))
    story.append(Paragraph("• <b>Slow Venue Ingress:</b> Manual paper roster verification causes severe congestion and bottlenecks at entrance gates.", bullet_style))
    story.append(Paragraph("• <b>Unverified Organizers:</b> Unregulated accounts can publish unapproved events, leading to schedule conflicts and unauthorized facility use.", bullet_style))
    story.append(Paragraph("• <b>Absence of Centralized Data:</b> Institutional leadership lacks real-time insight into student engagement, club activity levels, and venue utilization.", bullet_style))

    story.append(Paragraph("<b>4.2 Proposed System</b>", h2_style))
    story.append(Paragraph(
        "The Smart Campus Event Management System introduces an automated, end-to-end digital lifecycle that interconnects students, clubs, and campus governance into a single secure platform. Organizers must be approved by campus authorities before proposing events, and proposals undergo administrative review with recorded feedback.",
        body_style
    ))
    story.append(Paragraph("<b>Advantages of the Proposed System:</b>", h3_style))
    story.append(Paragraph("• <b>Role-Isolated Workspaces:</b> Dedicated dashboards for Students, Organizers, and Admins tailored to specific workflows.", bullet_style))
    story.append(Paragraph("• <b>Zero Overbooking:</b> Atomic database conditional increments eliminate reservation race conditions under simultaneous bookings.", bullet_style))
    story.append(Paragraph("• <b>Tamper-Proof QR Tickets:</b> Encrypted digital passes issued directly to student accounts with cryptographic ticket hashes.", bullet_style))
    story.append(Paragraph("• <b>High-Speed Gate Scanning:</b> Fast single-scan verification prevents duplicate entry and automates attendance timestamps.", bullet_style))
    story.append(Paragraph("• <b>Real-Time Governance:</b> Instant administrative moderation and analytics aggregation across all university departments.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: 5. SYSTEM DESIGN - 5.1
    # =========================================================================
    story.append(Paragraph("<b>5. SYSTEM DESIGN</b>", h1_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>5.1 System Architecture</b>", h2_style))
    story.append(Paragraph(
        "The Smart Campus platform follows a three-tier web application architecture comprising the <b>Presentation Layer</b>, <b>Application / Business Logic Layer</b>, and <b>Persistence Layer</b>. The frontend communicates with the backend exclusively through asynchronous JSON-based REST APIs authenticated via JWT Bearer headers.",
        body_style
    ))
    story.append(Paragraph(
        "The presentation tier delivers role-specific interfaces: the Student Dashboard for browsing and pass management, the Organizer Dashboard for proposal creation and venue check-in, and the Central Admin Console for institutional governance. The Express.js application tier validates requests, enforces role authorization guards, generates cryptographic QR codes, and executes atomic booking transactions against the MongoDB persistence tier.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: FIGURE 5.1 SYSTEM ARCHITECTURE DIAGRAM
    # =========================================================================
    story.append(Paragraph("<b>5.1 System Architecture (Diagram)</b>", h2_style))
    story.append(Paragraph(
        "The diagram illustrates the layered interaction between the client browser, the Express.js routing and middleware tier, the business logic controllers, and the underlying MongoDB document database.",
        body_style
    ))
    story.extend(create_diagram_frame("5.1 SYSTEM ARCHITECTURE DIAGRAM", "Figure 5.1: High-level architectural tiers of the Smart Campus Event Management System.", height=450))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: 5.1 ARCHITECTURE LAYERS & 5.2 USE CASE INTRO
    # =========================================================================
    story.append(Paragraph("<b>Main Architecture Layers</b>", h2_style))
    arch_rows = [
        [Paragraph("<b>Layer</b>", th_style), Paragraph("<b>Components & Responsibilities</b>", th_style)],
        [Paragraph("Presentation Layer", td_bold), Paragraph("HTML5, CSS3, Vanilla JS, Bootstrap 5. Provides role-specific views (Student, Organizer, Admin dashboards), event catalog, and QR ticket modal.", td_style)],
        [Paragraph("Application Layer", td_bold), Paragraph("Node.js / Express.js REST API. Manages routing, JWT token verification, RBAC middleware, atomic seat booking logic, QR generation, and gate check-in.", td_style)],
        [Paragraph("Analysis & Logic", td_bold), Paragraph("Atomic seat capacity evaluator, duplicate ticket detection algorithm, and approval workflow controller.", td_style)],
        [Paragraph("Persistence Layer", td_bold), Paragraph("MongoDB with Mongoose schemas (User, Department, Category, Event, Registration, Ticket). Enforces indexing, constraints, and aggregation.", td_style)]
    ]
    t_arch = Table(arch_rows, colWidths=[120, 384])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>5.2 Use Case Diagram</b>", h2_style))
    story.append(Paragraph(
        "The primary actors are <b>Student</b>, <b>Event Organizer</b>, and <b>Administrator</b>. Students can browse approved events, register seats, view QR tickets, and cancel bookings. Organizers can propose events, view attendee rosters, and scan tickets. Administrators can approve/reject organizer accounts, moderate event proposals, and govern user access.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: FIGURE 5.2 USE CASE DIAGRAM
    # =========================================================================
    story.append(Paragraph("<b>5.2 Use Case Diagram (Diagram)</b>", h2_style))
    story.extend(create_diagram_frame("5.2 USE CASE DIAGRAM", "Figure 5.2: Use cases available to Students, Organizers, and Campus Administrators.", height=480))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: 5.3 CLASS DIAGRAM
    # =========================================================================
    story.append(Paragraph("<b>5.3 Class Diagram</b>", h2_style))
    story.append(Paragraph(
        "The implementation structure is organized around core domain models and controller routers. The User entity represents all actors; Department and Category normalize taxonomies; Event encapsulates scheduling and seat capacity; Registration maintains the unique binding; and Ticket represents the digital pass. The diagram depicts the classes, attributes, methods, and database relationships.",
        body_style
    ))
    story.extend(create_diagram_frame("5.3 CLASS / SCHEMA DIAGRAM", "Figure 5.3: Main classes, schemas, and relationships in the implementation.", height=460))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 14: 5.4 SEQUENCE DIAGRAM
    # =========================================================================
    story.append(Paragraph("<b>5.4 Sequence Diagram</b>", h2_style))
    story.append(Paragraph(
        "The sequence below illustrates the end-to-end event registration and ticket generation flow. The student submits a booking request from the client browser. The Express router verifies the JWT, invokes the atomic seat reservation engine in MongoDB, generates the QR code pass, and returns the digital pass to the client viewport.",
        body_style
    ))
    story.extend(create_diagram_frame("5.4 SEQUENCE DIAGRAM — ATOMIC REGISTRATION & TICKET GENERATION", "Figure 5.4: Sequence of operations for student registration and QR ticket generation.", height=460))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 15: 5.5 ACTIVITY DIAGRAM
    # =========================================================================
    story.append(Paragraph("<b>5.5 Activity Diagram</b>", h2_style))
    story.append(Paragraph(
        "The activity diagram models the operational branching logic for event proposal moderation and physical venue check-in. It illustrates the decision pathways when an administrator reviews an event proposal and when an organizer scans a ticket at the entrance gate.",
        body_style
    ))
    story.extend(create_diagram_frame("5.5 ACTIVITY DIAGRAM — APPROVAL AND CHECK-IN WORKFLOW", "Figure 5.5: Activity flow for event proposal approval and gate check-in.", height=460))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 16: 6. METHODOLOGY - STATE MACHINE
    # =========================================================================
    story.append(Paragraph("<b>6. METHODOLOGY</b>", h1_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The Smart Campus Event Management System employs a state-driven engineering methodology to guarantee data consistency, role isolation, and verifiable event participation across all campus departments.",
        body_style
    ))
    story.append(Paragraph("<b>Event Lifecycle State Machine</b>", h2_style))
    story.append(Paragraph(
        "Every campus event transitions through well-defined operational states from initial proposal to completion:",
        body_style
    ))

    state_rows = [
        [Paragraph("<b>Status State</b>", th_style), Paragraph("<b>Trigger Condition</b>", th_style), Paragraph("<b>Operational Behavior</b>", th_style)],
        [Paragraph("PENDING", td_bold), Paragraph("Organizer creates event proposal.", td_style), Paragraph("Visible only to proposing organizer and administrators. Hidden from the student catalog.", td_style)],
        [Paragraph("APPROVED", td_bold), Paragraph("Administrator approves proposal.", td_style), Paragraph("Published to public catalog. Students can view details and register available seats.", td_style)],
        [Paragraph("REJECTED", td_bold), Paragraph("Administrator rejects proposal.", td_style), Paragraph("Archived with mandatory feedback explanation. Hidden from student catalog.", td_style)],
        [Paragraph("CANCELLED", td_bold), Paragraph("Organizer cancels scheduled event.", td_style), Paragraph("Registrations invalidated, ticket check-in locked, notification displayed.", td_style)]
    ]
    t_st = Table(state_rows, colWidths=[90, 150, 264])
    t_st.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_st)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 17: 6. METHODOLOGY - ATOMIC BOOKING & QR PROTOCOL
    # =========================================================================
    story.append(Paragraph("<b>High-Concurrency Atomic Seat Booking Algorithm</b>", h2_style))
    story.append(Paragraph(
        "To prevent race conditions where simultaneous student requests exceed room capacity, the reservation logic relies on a single atomic database operation. Rather than reading the count and issuing a subsequent write (a check-then-act anti-pattern), the system issues a conditional <code>findOneAndUpdate</code> query:",
        body_style
    ))
    story.append(Paragraph(
        "<code>Query: { _id: eventId, status: 'APPROVED', $expr: { $lt: ['$registeredCount', '$seatLimit'] } }</code><br/>"
        "<code>Update: { $inc: { registeredCount: 1 } }</code>",
        code_block
    ))
    story.append(Paragraph(
        "MongoDB executes this update with document-level locking. If the remaining seats reach zero, the condition fails atomically, returning null and rejecting subsequent bookings with zero overbooking risk.",
        body_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Cryptographic QR Pass & Check-In Protocol</b>", h2_style))
    story.append(Paragraph(
        "Upon seat reservation, the server generates a standardized ticket document. The payload combines the alphanumeric ticket code, unique event ID, student ID, and title. The <code>qrcode</code> engine converts this structure into a high-density Base64 PNG data URI rendered natively in browser viewports.",
        body_style
    ))
    story.append(Paragraph(
        "At the venue door, the organizer enters or scans the ticket ID. The verification algorithm queries the ticket, verifies organizer event ownership, and validates the <code>isCheckedIn</code> boolean. If true, the attempt is immediately flagged as a duplicate with the original scan timestamp. If false, it updates <code>isCheckedIn: true</code> and records <code>checkedInAt: Date()</code>.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 18: 6. METHODOLOGY - DATA STORAGE METHOD
    # =========================================================================
    story.append(Paragraph("<b>Data Storage and Audit Tracking Method</b>", h2_style))
    story.append(Paragraph(
        "The persistence tier leverages MongoDB document collections normalized to balance transactional speed with referential integrity. Each core activity produces traceable audit records:",
        body_style
    ))
    story.append(Paragraph("• <b>User Identity:</b> Stores encrypted passwords, role classifications (admin, organizer, student), department references, and organizer approval statuses (PENDING, APPROVED, REJECTED).", bullet_style))
    story.append(Paragraph("• <b>Event Records:</b> Captures venue coordinates, seat limit, current registration counter, status states, and administrative rejection rationale.", bullet_style))
    story.append(Paragraph("• <b>Registration Records:</b> Connects student accounts with specific events. A unique compound index on <code>(event, student)</code> strictly enforces single-pass rules at the database engine level.", bullet_style))
    story.append(Paragraph("• <b>Ticket Records:</b> Stores unique ticket codes (e.g., <code>EVT-HACK26-ALEX1</code>), Base64 QR code representations, gate check-in booleans, and exact verification timestamps.", bullet_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "This relational referencing model ensures that department name updates or event reschedulings propagate automatically without duplicate or stale records across the platform.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 19: 7. IMPLEMENTATION - TECH STACK & MODULES
    # =========================================================================
    story.append(Paragraph("<b>7. IMPLEMENTATION</b>", h1_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The application is implemented as a Node.js Express REST API paired with a vanilla JavaScript and Bootstrap 5 frontend. It runs locally at <code>http://localhost:5000</code>.",
        body_style
    ))
    story.append(Paragraph("<b>Technology Stack</b>", h2_style))

    tech_rows = [
        [Paragraph("<b>Technology</b>", th_style), Paragraph("<b>Role in Smart Campus Platform</b>", th_style)],
        [Paragraph("Node.js LTS", td_bold), Paragraph("Asynchronous server runtime environment executing backend services.", td_style)],
        [Paragraph("Express.js", td_bold), Paragraph("REST API routing, request validation, middleware pipeline, and static file hosting.", td_style)],
        [Paragraph("MongoDB / Mongoose", td_bold), Paragraph("Document database persistence, compound unique constraints, and population schemas.", td_style)],
        [Paragraph("JSON Web Tokens (JWT)", td_bold), Paragraph("Cryptographically signed authorization tokens stored in localStorage and sent via Bearer headers.", td_style)],
        [Paragraph("bcryptjs", td_bold), Paragraph("One-way salted password hashing for credential confidentiality.", td_style)],
        [Paragraph("qrcode npm", td_bold), Paragraph("Dynamic 2D matrix barcode rendering for digital student entry passes.", td_style)],
        [Paragraph("Bootstrap 5 & Icons CDN", td_bold), Paragraph("Responsive grid layout, modern typography, modal dialogs, and SVG iconography.", td_style)]
    ]
    t_tc = Table(tech_rows, colWidths=[130, 374])
    t_tc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_tc)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Module & File Organization</b>", h2_style))
    mod_rows = [
        [Paragraph("<b>File / Module</b>", th_style), Paragraph("<b>Responsibility</b>", th_style)],
        [Paragraph("backend/server.js", td_bold), Paragraph("Initializes Express, connects to MongoDB, mounts API routes, and serves frontend static assets.", td_style)],
        [Paragraph("backend/config/db.js", td_bold), Paragraph("Manages Mongoose connection lifecycle, handles reconnects, and logs connection telemetry.", td_style)],
        [Paragraph("backend/middleware/auth.js", td_bold), Paragraph("Enforces JWT verification, role-based authorization guards, and organizer approval vetting.", td_style)],
        [Paragraph("backend/routes/authRoutes.js", td_bold), Paragraph("Endpoints for user registration, multi-role login, user profile updates, and department listings.", td_style)],
        [Paragraph("backend/routes/eventRoutes.js", td_bold), Paragraph("Event CRUD, atomic registration, QR generation, attendee roster, and gate check-in counter.", td_style)],
        [Paragraph("backend/routes/adminRoutes.js", td_bold), Paragraph("Admin metrics aggregation, organizer vetting (Approve/Reject), user activation toggles.", td_style)],
        [Paragraph("backend/scripts/seed.js", td_bold), Paragraph("Idempotent database seeding for departments, categories, admin, test organizers, and events.", td_style)],
        [Paragraph("frontend/js/api.js", td_bold), Paragraph("Shared fetch wrapper injecting Bearer tokens, handling errors, and displaying global toast alerts.", td_style)],
        [Paragraph("frontend/js/auth.js", td_bold), Paragraph("Session state management, role-based client routing guards, and dynamic navbar injection.", td_style)]
    ]
    t_md = Table(mod_rows, colWidths=[140, 364])
    t_md.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_md)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 20: 7. IMPLEMENTATION - ROUTES & DATABASE DESIGN
    # =========================================================================
    story.append(Paragraph("<b>REST Application Routes</b>", h2_style))
    route_rows = [
        [Paragraph("<b>HTTP Route</b>", th_style), Paragraph("<b>Role Guard</b>", th_style), Paragraph("<b>Functional Purpose</b>", th_style)],
        [Paragraph("POST /api/auth/register", td_bold), Paragraph("Public", td_style), Paragraph("Registers Student or Organizer account (Organizer starts PENDING).", td_style)],
        [Paragraph("POST /api/auth/login", td_bold), Paragraph("Public", td_style), Paragraph("Authenticates credentials and returns JWT session token and user payload.", td_style)],
        [Paragraph("GET /api/auth/me", td_bold), Paragraph("Authenticated", td_style), Paragraph("Retrieves current authenticated session user and profile details.", td_style)],
        [Paragraph("GET /api/events", td_bold), Paragraph("Public", td_style), Paragraph("Retrieves approved campus events with optional category and search filters.", td_style)],
        [Paragraph("POST /api/events", td_bold), Paragraph("Approved Organizer", td_style), Paragraph("Submits a new event proposal to the admin moderation queue.", td_style)],
        [Paragraph("POST /api/events/:id/register", td_bold), Paragraph("Student", td_style), Paragraph("Executes atomic seat reservation and generates QR digital ticket pass.", td_style)],
        [Paragraph("POST /api/events/checkin", td_bold), Paragraph("Approved Organizer", td_style), Paragraph("Scans ticket ID at venue door and prevents duplicate admission.", td_style)],
        [Paragraph("GET /api/admin/stats", td_bold), Paragraph("Admin", td_style), Paragraph("Aggregates system-wide counts: students, organizers, events, and bookings.", td_style)],
        [Paragraph("PATCH /api/admin/organizers/:id/approval", td_bold), Paragraph("Admin", td_style), Paragraph("Approves or rejects organizer accounts with required feedback.", td_style)],
        [Paragraph("PATCH /api/events/:id/review", td_bold), Paragraph("Admin", td_style), Paragraph("Approves or rejects pending event proposals.", td_style)]
    ]
    t_rt = Table(route_rows, colWidths=[150, 100, 254])
    t_rt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_rt)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Database Schema Design</b>", h2_style))
    db_rows = [
        [Paragraph("<b>Collection</b>", th_style), Paragraph("<b>Key Fields & Types</b>", th_style), Paragraph("<b>Design Rationale & Indexes</b>", th_style)],
        [Paragraph("User", td_bold), Paragraph("name, email (unique), password, role (Enum), approvalStatus (Enum)", td_style), Paragraph("Normalizes all campus actors. Indexed on email (unique) and role.", td_style)],
        [Paragraph("Department", td_bold), Paragraph("name (unique), timestamps", td_style), Paragraph("Centralizes academic department classifications across the university.", td_style)],
        [Paragraph("Category", td_bold), Paragraph("name (unique), timestamps", td_style), Paragraph("Categorizes events (Technology, Culture, Sports, Workshop, Seminar).", td_style)],
        [Paragraph("Event", td_bold), Paragraph("organizer, category, title, venue, eventDate, seatLimit, registeredCount, status", td_style), Paragraph("Encapsulates event lifecycle. Indexed on status, eventDate, and category.", td_style)],
        [Paragraph("Registration", td_bold), Paragraph("event (Ref), student (Ref), status (Enum), registeredAt (Date)", td_style), Paragraph("Compound unique index on (event, student) enforces single ticket per student.", td_style)],
        [Paragraph("Ticket", td_bold), Paragraph("registration (Ref, unique), ticketId (unique), qrCodeDataUrl, isCheckedIn", td_style), Paragraph("Represents verified admission pass. Indexed on unique ticketId.", td_style)]
    ]
    t_dbs = Table(db_rows, colWidths=[80, 210, 214])
    t_dbs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_dbs)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 21: 7. IMPLEMENTATION - UI, EXECUTION & TESTING
    # =========================================================================
    story.append(Paragraph("<b>User Interface Implementation</b>", h2_style))
    story.append(Paragraph(
        "The user interface uses Bootstrap 5 CDN components and custom CSS3 variables to achieve a modern, responsive layout. The navigation bar dynamically adjusts its displayed links based on user role (Student, Organizer, or Admin). Event cards incorporate CSS gradients, category badges, and seats-left progress bars. The ticket pass displays a realistic event pass layout with perforated border cutouts, barcode styling, and embedded QR code imagery.",
        body_style
    ))
    story.append(Paragraph("<b>Installation and Execution</b>", h2_style))
    story.append(Paragraph(
        "The following commands describe the setup executed in Windows PowerShell or the VS Code terminal from the project root directory:",
        body_style
    ))
    story.append(Paragraph(
        "<code># 1. Install Node.js dependencies</code><br/>"
        "<code>npm install</code><br/><br/>"
        "<code># 2. Seed database with Admin, categories, departments, and demo accounts</code><br/>"
        "<code>npm run seed</code><br/><br/>"
        "<code># 3. Start development server with live reload</code><br/>"
        "<code>npm run dev</code>",
        code_block
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Testing</b>", h2_style))
    t_cases = [
        [Paragraph("<b>Test Case</b>", th_style), Paragraph("<b>Input / Action</b>", th_style), Paragraph("<b>Expected Result</b>", th_style), Paragraph("<b>Observed Result</b>", th_style)],
        [Paragraph("Admin Seeding", td_bold), Paragraph("Run seed script with .env credentials", td_style), Paragraph("Admin created without duplicates; Admin dashboard loads.", td_style), Paragraph("Passed", td_bold)],
        [Paragraph("Organizer Vetting", td_bold), Paragraph("Register new club; sign in before Admin approval", td_style), Paragraph("Dashboard shows PENDING status banner; creation locked.", td_style), Paragraph("Passed", td_bold)],
        [Paragraph("Event Moderation", td_bold), Paragraph("Admin approves pending event proposal", td_style), Paragraph("Status updates to APPROVED; event appears in catalog.", td_style), Paragraph("Passed", td_bold)],
        [Paragraph("Atomic Booking", td_bold), Paragraph("Student registers for event with seats available", td_style), Paragraph("Seat count decrements atomically; QR pass generated.", td_style), Paragraph("Passed", td_bold)],
        [Paragraph("Overbooking Guard", td_bold), Paragraph("Attempt booking when registeredCount = seatLimit", td_style), Paragraph("Server returns 400 error: Event full; booking rejected.", td_style), Paragraph("Passed", td_bold)],
        [Paragraph("Gate QR Check-In", td_bold), Paragraph("Organizer scans ticket ID EVT-HACK26-ALEX1 at door", td_style), Paragraph("Admission verified; check-in timestamp saved in database.", td_style), Paragraph("Passed", td_bold)]
    ]
    t_tc_tbl = Table(t_cases, colWidths=[90, 130, 210, 74])
    t_tc_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TEXTCOLOR', (3,1), (3,-1), colors.HexColor("#15803d"))
    ]))
    story.append(t_tc_tbl)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 22: 8. OUTPUT SCREENSHOTS (PAGE 1)
    # =========================================================================
    story.append(Paragraph("<b>8. OUTPUT SCREENSHOTS</b>", h1_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "This section is reserved for screenshots captured from the final running Smart Campus Event Management System. Labeled frame placeholders are provided below for the project author to insert actual application screen captures prior to final university submission.",
        body_style
    ))
    story.extend(create_diagram_frame("SCREENSHOT: LANDING HOME PAGE & MULTI-ROLE PORTAL", "Figure 8.1: Landing home page showing campus activities and multi-role navigation portal.", height=255))
    story.extend(create_diagram_frame("SCREENSHOT: TRI-ROLE AUTHENTICATION (STUDENT / ORGANIZER / ADMIN)", "Figure 8.2: Multi-role authentication interface with Student, Organizer, and Admin login tabs.", height=255))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 23: 8. OUTPUT SCREENSHOTS (PAGE 2)
    # =========================================================================
    story.append(Paragraph("<b>8. Output Screenshots (Continued)</b>", h2_style))
    story.extend(create_diagram_frame("SCREENSHOT: STUDENT DASHBOARD & DISCOVER EVENTS", "Figure 8.3: Student Dashboard displaying registered passes, upcoming activity metrics, and available events.", height=270))
    story.extend(create_diagram_frame("SCREENSHOT: DIGITAL EVENT PASS & CRYPTOGRAPHIC QR CODE", "Figure 8.4: Official digital event pass modal featuring unique alphanumeric code and Base64 QR code.", height=270))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 24: 8. OUTPUT SCREENSHOTS (PAGE 3)
    # =========================================================================
    story.append(Paragraph("<b>8. Output Screenshots (Continued)</b>", h2_style))
    story.extend(create_diagram_frame("SCREENSHOT: ORGANIZER DASHBOARD & ATTENDEE CHECK-IN DESK", "Figure 8.5: Organizer Dashboard showing account approval status, event management, and gate check-in tool.", height=270))
    story.extend(create_diagram_frame("SCREENSHOT: CENTRAL ADMINISTRATION CONSOLE", "Figure 8.6: Central Administration Console displaying pending organizer approvals, proposal review, and metrics.", height=270))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 25: 9. CONCLUSION
    # =========================================================================
    story.append(Paragraph("<b>9. CONCLUSION</b>", h1_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The <b>Smart Campus Event Management System</b> demonstrates the design, engineering, and implementation of a modern, multi-tier web platform for higher education institutions. By integrating role-based authentication, formal administrative vetting workflows, concurrency-safe atomic seat booking, and digital QR ticket verification, the system resolves longstanding campus challenges including venue overbooking, unapproved event publication, and proxy attendance.",
        body_style
    ))
    story.append(Paragraph(
        "The project rigorously fulfills modern Software Engineering paradigms. The RESTful architecture cleanly decouples client and server responsibilities; MongoDB atomic operators ensure transaction-like data consistency without heavy distributed transaction overhead; and the vanilla JavaScript/Bootstrap 5 frontend delivers responsive, lightweight performance across all client devices without client-side framework complexity.",
        body_style
    ))
    story.append(Paragraph("<b>Limitations and Future Enhancements:</b>", h2_style))
    story.append(Paragraph(
        "While the current implementation provides a complete, working operational foundation, future development can further expand the system capabilities:",
        body_style
    ))
    story.append(Paragraph("• <b>Automated Certificate Generation:</b> Dynamically generating and emailing verifiable PDF participation certificates to attendees whose tickets were scanned at the venue gate.", bullet_style))
    story.append(Paragraph("• <b>Mobile Native Scanner App:</b> Developing a companion React Native / Flutter mobile application leveraging native device cameras for rapid barcode scanning in offline mode.", bullet_style))
    story.append(Paragraph("• <b>Automated Email & Push Notifications:</b> Integrating SMTP services (Nodemailer) and Web Push notifications to remind students of upcoming event schedules.", bullet_style))
    story.append(Paragraph("• <b>Facility Resource Management:</b> Expanding the admin portal to manage physical sound equipment, stage lighting, and auditorium maintenance schedules.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 26: 10. REFERENCES
    # =========================================================================
    story.append(Paragraph("<b>10. REFERENCES</b>", h1_style))
    story.append(Spacer(1, 10))

    references = [
        "[1] OpenJS Foundation, “Node.js LTS Documentation,” Available: https://nodejs.org/en/docs/ (Accessed: November 2026).",
        "[2] Express.js, “Express - Fast, unopinionated, minimalist web framework for Node.js,” Available: https://expressjs.com/ (Accessed: November 2026).",
        "[3] MongoDB Inc., “MongoDB Manual - Document Databases and Atomic Operations,” Available: https://www.mongodb.com/docs/manual/ (Accessed: November 2026).",
        "[4] Automattic, “Mongoose ODM v8 Documentation,” Available: https://mongoosejs.com/docs/ (Accessed: November 2026).",
        "[5] M. Jones, J. Bradley, and N. Sakimura, “JSON Web Token (JWT),” RFC 7519, Internet Engineering Task Force (IETF), May 2015. Available: https://www.rfc-editor.org/rfc/rfc7519.",
        "[6] International Organization for Standardization, “ISO/IEC 18004:2015 - Information technology — Automatic identification and data capture techniques — QR Code bar code symbology specification,” ISO, 2015.",
        "[7] Bootstrap Authors, “Bootstrap v5.3 Documentation,” Available: https://getbootstrap.com/docs/5.3/ (Accessed: November 2026).",
        "[8] ReportLab Inc., “ReportLab PDF Generation Library Documentation,” Available: https://docs.reportlab.com/ (Accessed: November 2026).",
        "[9] Smart Campus Event Management System Source Code Repository, including Express REST controllers, Mongoose schemas, auth middleware, and responsive frontend dashboards. Project implementation package, Version 1.0, 2026."
    ]

    for ref in references:
        story.append(Paragraph(ref, ParagraphStyle('RefStyle', fontName='Helvetica', fontSize=8.5, leading=13.5, spaceAfter=8, textColor=colors.HexColor("#1e293b"))))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF successfully generated: {os.path.abspath(filename)}")

if __name__ == '__main__':
    build_pdf()
