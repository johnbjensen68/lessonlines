# LessonLines Product Summary

## Value Proposition

Teachers need timelines for their classrooms, but existing tools only solve half the problem. Current timeline makers provide a blank canvas where teachers must research, gather, and enter every historical event themselves. This is time-consuming work that pulls teachers away from what they do best: teaching.

LessonLines combines a simple, intuitive timeline builder with a curated database of historical events aligned to common school curricula. Teachers can search for a topic, filter by curriculum standard, select relevant events, and build a polished timeline in minutes rather than hours.

**Core promise:** Timelines in minutes, not hours.

---

## Target Market

**Primary audience:** K-12 teachers, particularly those teaching history and social studies.

| Factor | Why It Matters |
|--------|----------------|
| Willingness to pay | Teachers regularly spend their own money on classroom materials ($400-700/year on average) |
| Time-constrained | Teachers value tools that save preparation time, making a curated database highly attractive |
| Word of mouth | Teachers share resources with colleagues, enabling organic growth within schools and districts |
| Reusable content | A timeline created once can be used year after year, making a one-time purchase feel worthwhile |
| Curriculum alignment | Teachers need materials that map to specific standards they're required to teach |

---

## Primary Features

### Timeline Builder

A web-based tool that allows teachers to create timelines by adding events manually or by pulling from the curated database.

**Core functionality:**
- Search and filter events by topic, curriculum standard, grade level, or keyword
- Drag events from the database onto the timeline
- Add custom events for content not in the database
- Basic styling options (colors, layout, fonts)
- Save projects for later editing
- Export to PDF or image formats (pro feature)

### Curated Historical Database

A searchable database of historical events organized by topic and aligned to common curricula.

**Each event includes:**
- Date (with precision indicator: exact day, month, year, or circa)
- Title and description
- Location
- Significance (why this event matters)
- Source attribution
- Tags for flexible categorization
- Alignment to curriculum standards

### Curriculum Standards Alignment

Events are mapped to curriculum standards so teachers can find content that matches what they're required to teach.

**Supported frameworks (at launch):**
- Common Core State Standards
- AP US History
- Texas TEKS (as an example state standard)

**Teachers can:**
- Filter events by curriculum framework
- Filter by grade level
- See which standards a timeline covers
- Find events that align to specific standards they need to address

### Launch Topics

Starting narrow and deep with 2-3 well-curated topics:
- American Civil War
- American Revolution
- World War II

Additional topics will be added based on teacher requests.

---

## Business Model

### Pricing Structure

A freemium model with a one-time purchase for the full product:

| Tier | Features | Price |
|------|----------|-------|
| Free | Basic timeline creation, limited exports (watermarked or low-resolution) | $0 |
| Pro | Unlimited exports, no watermark, full access to curated database, additional customization | $25-35 (one-time) |

### Why One-Time Purchase

A one-time purchase model was chosen over subscriptions for simplicity:

- Teachers prefer not to manage recurring expenses
- One-time fee reduces friction at the point of sale
- Simplifies operations for a single-person company
- No subscription management, failed payment handling, or churn tracking
- Teachers can justify a single purchase more easily than ongoing costs

### Payment Processing

Stripe or Gumroad for simple, self-serve checkout with no sales calls required.

---

## Competitive Landscape

The market has many timeline creation tools:
- Preceden
- Timepath
- Timetoast
- Time.Graphics
- Tiki-Toki
- Timeline JS
- Canva

**Gap in the market:** Most are blank-canvas tools where teachers build everything from scratch. None emphasize a searchable, curated database of historical events as a core feature.

**LessonLines differentiator:** The combination of a simple web-based editor plus a deep, curriculum-aligned event database. The tool is table stakes; the curated content is the real value.

---

## Competitive Advantages

1. **Curated content saves time** — Teachers don't just need a tool, they need the content itself
2. **Curriculum alignment** — Events mapped to standards teachers are required to teach
3. **Simple pricing** — One-time purchase respects teacher budgets
4. **Focused on education** — Purpose-built for K-12, not a general-purpose tool
5. **Quality over quantity** — Deeply researched topics rather than shallow coverage

---

## Domain

**lessonlines.com** — Available and recommended for purchase.

---

## Next Steps

1. Purchase domain (Cloudflare, Namecheap, or Route 53)
2. Set up AWS infrastructure (VPC, RDS PostgreSQL, Lambda, API Gateway)
3. Build the FastAPI backend with event and timeline endpoints
4. Create seed data for first topic (Civil War) with curriculum alignments
5. Build the React frontend with timeline editor
6. Integrate Stripe for pro purchases
7. Launch and gather feedback from teachers
8. Add additional topics based on demand

---

## Reference Documents

- **lessonlines_technical_spec.md** — Full technical architecture, database schema, API endpoints, and implementation phases
- **timeline_ui_mockup.html** — Visual design reference for the teacher-facing timeline builder
- **admin_ui_mockup.html** — Visual design reference for the admin event management interface
