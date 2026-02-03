# LessonLines Technical Specification

## Overview

LessonLines is a web application that helps K-12 teachers create historical timelines quickly by providing a curated database of historical events they can search and drag onto a timeline builder.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                    (React + Amplify Hosting)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Lambda (FastAPI + Mangum)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        RDS Proxy                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  RDS PostgreSQL (Database)                       │
└─────────────────────────────────────────────────────────────────┘
```

**Note:** RDS Proxy is used between Lambda and PostgreSQL to manage connection pooling, which is essential for serverless workloads that can spin up many concurrent connections.

## Project Structure

```
lessonlines/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar/
│   │   │   │   ├── EventDatabase.tsx      # Left panel with searchable events
│   │   │   │   ├── EventCard.tsx          # Draggable event card
│   │   │   │   └── TopicTabs.tsx          # Topic filter tabs
│   │   │   ├── Timeline/
│   │   │   │   ├── TimelineCanvas.tsx     # Main timeline display
│   │   │   │   ├── TimelineEvent.tsx      # Event on the timeline
│   │   │   │   ├── DropZone.tsx           # Drag target area
│   │   │   │   └── TimelineLine.tsx       # The visual line
│   │   │   ├── Toolbar/
│   │   │   │   ├── Toolbar.tsx            # Top toolbar container
│   │   │   │   ├── ColorPicker.tsx        # Timeline color options
│   │   │   │   ├── LayoutToggle.tsx       # Horizontal/vertical toggle
│   │   │   │   └── ExportButton.tsx       # PDF export (pro feature)
│   │   │   └── common/
│   │   │       ├── Header.tsx
│   │   │       └── Button.tsx
│   │   ├── pages/
│   │   │   ├── Editor.tsx                 # Main timeline editor page
│   │   │   ├── MyTimelines.tsx            # User's saved timelines
│   │   │   ├── Landing.tsx                # Marketing landing page
│   │   │   └── Login.tsx
│   │   ├── hooks/
│   │   │   ├── useTimeline.ts             # Timeline state management
│   │   │   ├── useEvents.ts               # Event database queries
│   │   │   └── useDragDrop.ts             # Drag and drop logic
│   │   ├── api/
│   │   │   └── client.ts                  # API client functions
│   │   ├── types/
│   │   │   └── index.ts                   # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py                        # FastAPI app + Mangum handler
│   │   ├── routers/
│   │   │   ├── events.py                  # Event database endpoints
│   │   │   ├── timelines.py               # Timeline CRUD endpoints
│   │   │   ├── users.py                   # User management
│   │   │   ├── standards.py               # Curriculum standards endpoints
│   │   │   └── export.py                  # PDF export endpoint
│   │   ├── models/
│   │   │   ├── event.py                   # Event SQLAlchemy model
│   │   │   ├── timeline.py                # Timeline SQLAlchemy model
│   │   │   ├── user.py                    # User SQLAlchemy model
│   │   │   ├── standard.py                # Curriculum standard model
│   │   │   └── base.py                    # SQLAlchemy base and session
│   │   ├── schemas/
│   │   │   ├── event.py                   # Pydantic schemas for events
│   │   │   ├── timeline.py                # Pydantic schemas for timelines
│   │   │   ├── user.py                    # Pydantic schemas for users
│   │   │   └── standard.py                # Pydantic schemas for standards
│   │   ├── services/
│   │   │   ├── database.py                # Database connection and session
│   │   │   ├── pdf_export.py              # PDF generation logic
│   │   │   └── auth.py                    # Authentication helpers
│   │   └── config.py                      # Environment config
│   ├── migrations/
│   │   ├── versions/                      # Alembic migration files
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── tests/
│   │   ├── test_events.py
│   │   ├── test_timelines.py
│   │   └── conftest.py
│   ├── requirements.txt
│   └── template.yaml                      # SAM template
│
├── data/
│   ├── seed/
│   │   ├── civil_war.json                 # Curated Civil War events
│   │   ├── american_revolution.json       # Curated Revolution events
│   │   └── world_war_2.json               # Curated WWII events
│   └── scripts/
│       └── seed_database.py               # Script to populate DynamoDB
│
├── agent/                                 # Event curation AI agent (future)
│   ├── scraper.py
│   └── curator.py
│
└── README.md
```

## Database Schema (PostgreSQL)

### Topics

```sql
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(100) UNIQUE NOT NULL,          -- e.g., "civil_war"
    name VARCHAR(255) NOT NULL,                  -- e.g., "American Civil War"
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Curriculum Standards

```sql
CREATE TABLE curriculum_frameworks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,            -- e.g., "CCSS", "TEKS", "AP_USH"
    name VARCHAR(255) NOT NULL,                  -- e.g., "Common Core State Standards"
    state VARCHAR(50),                           -- e.g., "TX" for Texas, NULL for national
    subject VARCHAR(100),                        -- e.g., "Social Studies", "History"
    grade_levels VARCHAR(50),                    -- e.g., "K-12", "9-12", "6-8"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE curriculum_standards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_id UUID NOT NULL REFERENCES curriculum_frameworks(id),
    code VARCHAR(100) NOT NULL,                  -- e.g., "CCSS.ELA-LITERACY.RH.6-8.7"
    title VARCHAR(500) NOT NULL,                 -- Short title
    description TEXT,                            -- Full standard text
    grade_level VARCHAR(20),                     -- e.g., "8", "6-8", "HS"
    strand VARCHAR(255),                         -- e.g., "Reading", "Historical Thinking"
    parent_id UUID REFERENCES curriculum_standards(id), -- For hierarchical standards
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(framework_id, code)
);

CREATE INDEX idx_standards_framework ON curriculum_standards(framework_id);
CREATE INDEX idx_standards_grade ON curriculum_standards(grade_level);
```

### Events (curated historical events)

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID NOT NULL REFERENCES topics(id),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    date_start DATE NOT NULL,
    date_end DATE,                               -- NULL for single-day events
    date_display VARCHAR(100) NOT NULL,          -- Human-readable: "April 12, 1861"
    date_precision VARCHAR(20) DEFAULT 'day',    -- 'day', 'month', 'year', 'decade', 'circa'
    location VARCHAR(255),                       -- e.g., "Charleston, South Carolina"
    latitude DECIMAL(10, 8),                     -- For future map features
    longitude DECIMAL(11, 8),
    significance TEXT,                           -- Why this event matters
    source_url TEXT,
    source_citation TEXT,                        -- Formatted citation
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_topic ON events(topic_id);
CREATE INDEX idx_events_date ON events(date_start);
CREATE INDEX idx_events_search ON events USING gin(to_tsvector('english', title || ' ' || description));
```

### Event Tags (flexible categorization)

```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,           -- e.g., "military", "political", "social"
    category VARCHAR(50)                         -- e.g., "theme", "region", "figure"
);

CREATE TABLE event_tags (
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, tag_id)
);

CREATE INDEX idx_event_tags_tag ON event_tags(tag_id);
```

### Event-Standard Alignments

```sql
CREATE TABLE event_standards (
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    standard_id UUID NOT NULL REFERENCES curriculum_standards(id) ON DELETE CASCADE,
    alignment_notes TEXT,                        -- Optional explanation of alignment
    PRIMARY KEY (event_id, standard_id)
);

CREATE INDEX idx_event_standards_standard ON event_standards(standard_id);
```

### Users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cognito_id VARCHAR(255) UNIQUE NOT NULL,     -- From AWS Cognito
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    is_pro BOOLEAN DEFAULT FALSE,
    pro_purchased_at TIMESTAMP,
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Timelines (user-created)

```sql
CREATE TABLE timelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    subtitle VARCHAR(500),
    color_scheme VARCHAR(50) DEFAULT 'blue_green',
    layout VARCHAR(20) DEFAULT 'horizontal',     -- 'horizontal' or 'vertical'
    font VARCHAR(50) DEFAULT 'system',
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_timelines_user ON timelines(user_id);
```

### Timeline Events (events placed on a timeline)

```sql
CREATE TABLE timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timeline_id UUID NOT NULL REFERENCES timelines(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,  -- NULL if custom event
    position INTEGER NOT NULL,                   -- Order on timeline
    -- Custom event fields (used when event_id is NULL)
    custom_title VARCHAR(500),
    custom_description TEXT,
    custom_date_display VARCHAR(100),
    custom_date_start DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timeline_id, position)
);

CREATE INDEX idx_timeline_events_timeline ON timeline_events(timeline_id);
```

## SQLAlchemy Models

### Example: Event Model

```python
# app/models/event.py
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date)
    date_display = Column(String(100), nullable=False)
    date_precision = Column(String(20), default="day")
    location = Column(String(255))
    significance = Column(Text)
    source_url = Column(Text)
    source_citation = Column(Text)
    image_url = Column(Text)
    created_at = Column(DateTime, server_default="now()")
    updated_at = Column(DateTime, server_default="now()", onupdate="now()")

    # Relationships
    topic = relationship("Topic", back_populates="events")
    tags = relationship("Tag", secondary="event_tags", back_populates="events")
    standards = relationship("CurriculumStandard", secondary="event_standards", back_populates="events")

    __table_args__ = (
        Index("idx_events_topic", "topic_id"),
        Index("idx_events_date", "date_start"),
    )
```

### Example: CurriculumStandard Model

```python
# app/models/standard.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class CurriculumFramework(Base):
    __tablename__ = "curriculum_frameworks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    state = Column(String(50))
    subject = Column(String(100))
    grade_levels = Column(String(50))
    created_at = Column(DateTime, server_default="now()")

    standards = relationship("CurriculumStandard", back_populates="framework")


class CurriculumStandard(Base):
    __tablename__ = "curriculum_standards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework_id = Column(UUID(as_uuid=True), ForeignKey("curriculum_frameworks.id"), nullable=False)
    code = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    grade_level = Column(String(20))
    strand = Column(String(255))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("curriculum_standards.id"))
    created_at = Column(DateTime, server_default="now()")

    framework = relationship("CurriculumFramework", back_populates="standards")
    parent = relationship("CurriculumStandard", remote_side=[id], backref="children")
    events = relationship("Event", secondary="event_standards", back_populates="standards")
```

## Pydantic Schemas

### Event Schemas

```python
# app/schemas/event.py
from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional

class TagResponse(BaseModel):
    id: UUID
    name: str
    category: Optional[str]

    class Config:
        from_attributes = True

class StandardBrief(BaseModel):
    id: UUID
    code: str
    title: str
    framework_code: str
    grade_level: Optional[str]

    class Config:
        from_attributes = True

class EventResponse(BaseModel):
    id: UUID
    topic_id: UUID
    title: str
    description: str
    date_start: date
    date_end: Optional[date]
    date_display: str
    date_precision: str
    location: Optional[str]
    significance: Optional[str]
    source_url: Optional[str]
    source_citation: Optional[str]
    image_url: Optional[str]
    tags: list[TagResponse]
    standards: list[StandardBrief]
    created_at: datetime

    class Config:
        from_attributes = True

class EventListResponse(BaseModel):
    id: UUID
    title: str
    description: str
    date_display: str
    location: Optional[str]
    tags: list[TagResponse]

    class Config:
        from_attributes = True
```

## API Endpoints

### Events (curated database)

```
GET  /api/topics
     Returns list of available topics
     Response: [{ id, slug, name, description }, ...]

GET  /api/events?topic={slug}&q={search}&standard={standard_id}&tag={tag_name}&grade={grade}
     Search events with filters
     - topic: filter by topic slug
     - q: full-text search on title and description
     - standard: filter by curriculum standard ID
     - tag: filter by tag name
     - grade: filter by grade level (matches standards)
     Response: [EventListResponse, ...]

GET  /api/events/{event_id}
     Get single event with full details including standards
     Response: EventResponse
```

### Curriculum Standards

```
GET  /api/standards/frameworks
     Returns list of curriculum frameworks
     Response: [{ id, code, name, state, subject, grade_levels }, ...]

GET  /api/standards?framework={code}&grade={grade}&q={search}
     Search standards within a framework
     Response: [{ id, code, title, description, grade_level, strand }, ...]

GET  /api/standards/{standard_id}
     Get single standard with aligned events
     Response: { ...standard, events: [EventListResponse, ...] }
```

### Tags

```
GET  /api/tags?category={category}
     Returns list of tags, optionally filtered by category
     Response: [{ id, name, category }, ...]
```

### Timelines (user content)

```
GET  /api/timelines
     Get all timelines for authenticated user
     Response: [Timeline, Timeline, ...]

POST /api/timelines
     Create new timeline
     Body: { title, subtitle?, settings? }
     Response: Timeline

GET  /api/timelines/{timeline_id}
     Get single timeline
     Response: Timeline

PUT  /api/timelines/{timeline_id}
     Update timeline (title, events, settings)
     Body: { title?, subtitle?, events?, settings? }
     Response: Timeline

DELETE /api/timelines/{timeline_id}
       Delete timeline
       Response: 204 No Content

POST /api/timelines/{timeline_id}/events
     Add event to timeline
     Body: { event_id } or { title, description, date_display } for custom
     Response: Timeline

DELETE /api/timelines/{timeline_id}/events/{position}
       Remove event from timeline
       Response: Timeline

PUT  /api/timelines/{timeline_id}/events/reorder
     Reorder events on timeline
     Body: { positions: [event_id, event_id, ...] }
     Response: Timeline
```

### Export

```
POST /api/timelines/{timeline_id}/export/pdf
     Generate PDF of timeline (pro feature)
     Response: { download_url: "presigned S3 URL" }
```

### Users

```
GET  /api/users/me
     Get current user profile
     Response: User

POST /api/users/purchase
     Record pro purchase (called after Stripe webhook)
     Body: { stripe_session_id }
     Response: User
```

## Authentication

Use AWS Cognito for authentication:
- Email/password sign up and login
- JWT tokens passed in Authorization header
- Middleware validates token and extracts user_id

## Frontend State Management

Keep it simple with React hooks and context:

```typescript
// Timeline context for editor state
interface TimelineState {
    timeline: Timeline | null;
    isDirty: boolean;
    selectedEventPosition: number | null;
}

// Actions
type TimelineAction =
    | { type: 'LOAD_TIMELINE'; payload: Timeline }
    | { type: 'ADD_EVENT'; payload: TimelineEvent }
    | { type: 'REMOVE_EVENT'; payload: number }
    | { type: 'REORDER_EVENTS'; payload: string[] }
    | { type: 'UPDATE_SETTINGS'; payload: Partial<TimelineSettings> }
    | { type: 'UPDATE_TITLE'; payload: string };
```

## Key Frontend Features

### Drag and Drop
Use `@dnd-kit/core` for drag and drop:
- EventCard in sidebar is draggable
- DropZone accepts drops and adds to timeline
- Timeline events can be reordered by dragging

### Auto-save
Debounce saves to API when timeline changes:
```typescript
useEffect(() => {
    if (isDirty && timeline) {
        const timeout = setTimeout(() => {
            saveTimeline(timeline);
        }, 1000);
        return () => clearTimeout(timeout);
    }
}, [timeline, isDirty]);
```

### PDF Export
Pro feature - calls backend endpoint which:
1. Renders timeline to HTML
2. Uses WeasyPrint or similar to convert to PDF
3. Uploads to S3
4. Returns presigned download URL

## Infrastructure (SAM Template)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Parameters:
  DBUsername:
    Type: String
    Default: lessonlines_admin
  DBPassword:
    Type: String
    NoEcho: true
  VpcId:
    Type: AWS::EC2::VPC::Id
  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Globals:
  Function:
    Timeout: 30
    Runtime: python3.11
    MemorySize: 256
    VpcConfig:
      SecurityGroupIds:
        - !Ref LambdaSecurityGroup
      SubnetIds: !Ref PrivateSubnetIds

Resources:
  # API Gateway
  LessonLinesApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Cors:
        AllowOrigin: "'*'"
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"

  # Lambda Function
  LessonLinesFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: backend/
      Handler: app.main.handler
      Events:
        Api:
          Type: Api
          Properties:
            RestApiId: !Ref LessonLinesApi
            Path: /{proxy+}
            Method: ANY
      Environment:
        Variables:
          DATABASE_URL: !Sub 
            - "postgresql://${DBUsername}:${DBPassword}@${ProxyEndpoint}:5432/lessonlines"
            - ProxyEndpoint: !GetAtt RDSProxy.Endpoint
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - rds-db:connect
              Resource: !Sub "arn:aws:rds-db:${AWS::Region}:${AWS::AccountId}:dbuser:${RDSProxy}/${DBUsername}"

  # Security Groups
  LambdaSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Lambda functions
      VpcId: !Ref VpcId
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          DestinationSecurityGroupId: !Ref RDSSecurityGroup

  RDSSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref LambdaSecurityGroup

  # RDS PostgreSQL
  RDSSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for LessonLines RDS
      SubnetIds: !Ref PrivateSubnetIds

  RDSInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: lessonlines-db
      DBInstanceClass: db.t3.micro
      Engine: postgres
      EngineVersion: "15"
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      DBName: lessonlines
      AllocatedStorage: 20
      StorageType: gp2
      VPCSecurityGroups:
        - !Ref RDSSecurityGroup
      DBSubnetGroupName: !Ref RDSSubnetGroup
      PubliclyAccessible: false
      BackupRetentionPeriod: 7
      DeletionProtection: false  # Set to true for production

  # RDS Proxy (for Lambda connection pooling)
  RDSProxySecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: lessonlines-db-credentials
      SecretString: !Sub '{"username":"${DBUsername}","password":"${DBPassword}"}'

  RDSProxy:
    Type: AWS::RDS::DBProxy
    Properties:
      DBProxyName: lessonlines-proxy
      EngineFamily: POSTGRESQL
      Auth:
        - AuthScheme: SECRETS
          SecretArn: !Ref RDSProxySecret
          IAMAuth: DISABLED
      RoleArn: !GetAtt RDSProxyRole.Arn
      VpcSecurityGroupIds:
        - !Ref RDSSecurityGroup
      VpcSubnetIds: !Ref PrivateSubnetIds

  RDSProxyTargetGroup:
    Type: AWS::RDS::DBProxyTargetGroup
    Properties:
      DBProxyName: !Ref RDSProxy
      TargetGroupName: default
      DBInstanceIdentifiers:
        - !Ref RDSInstance

  RDSProxyRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: rds.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: RDSProxySecretsAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Ref RDSProxySecret

Outputs:
  ApiUrl:
    Value: !Sub "https://${LessonLinesApi}.execute-api.${AWS::Region}.amazonaws.com/prod"
  DatabaseEndpoint:
    Value: !GetAtt RDSInstance.Endpoint.Address
  ProxyEndpoint:
    Value: !GetAtt RDSProxy.Endpoint
```

**Note:** This template requires:
- A VPC with private subnets
- NAT Gateway for Lambda to access external services
- The database password should be stored in AWS Secrets Manager in production

## Development Workflow

### Local Development

```bash
# Start local PostgreSQL (using Docker)
docker run --name lessonlines-db \
  -e POSTGRES_USER=lessonlines \
  -e POSTGRES_PASSWORD=localdev \
  -e POSTGRES_DB=lessonlines \
  -p 5432:5432 \
  -d postgres:15

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed the database
python -m app.seed

# Start server
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Deployment

```bash
# Backend (SAM)
cd backend
sam build
sam deploy --guided

# Frontend (Amplify)
# Connect GitHub repo to Amplify console
# Auto-deploys on push to main
```

## Implementation Order

### Phase 1: Core Infrastructure
1. Set up VPC with public/private subnets and NAT Gateway
2. Set up RDS PostgreSQL instance
3. Set up RDS Proxy for connection pooling
4. Set up SAM project with Lambda + API Gateway
5. Implement FastAPI app with Mangum and SQLAlchemy
6. Create Alembic migrations for database schema
7. Set up Cognito user pool
8. Deploy and test basic auth flow

### Phase 2: Event Database & Standards
1. Define SQLAlchemy models for events, topics, tags, standards
2. Create seed data for curriculum frameworks (Common Core, AP US History, Texas TEKS)
3. Create seed data for Civil War topic (30-50 events)
4. Align events to relevant curriculum standards
5. Implement GET /api/events endpoints with filtering
6. Implement GET /api/standards endpoints
7. Test search and filter functionality

### Phase 3: Timeline CRUD
1. Implement timeline SQLAlchemy models
2. Create all timeline endpoints
3. Test full CRUD cycle

### Phase 4: Frontend MVP
1. Scaffold React app with Vite
2. Implement sidebar with event search and standard filtering
3. Implement timeline canvas
4. Implement drag and drop
5. Connect to API
6. Implement auto-save

### Phase 5: Polish
1. Add toolbar with styling options
2. Implement PDF export
3. Add landing page
4. Integrate Stripe for pro purchases
5. Add second and third topics to event database
6. Add more curriculum framework alignments

## Environment Variables

### Backend
```
DATABASE_URL=postgresql://user:password@proxy-endpoint:5432/lessonlines
COGNITO_USER_POOL_ID=us-east-1_xxxxx
COGNITO_APP_CLIENT_ID=xxxxx
S3_EXPORT_BUCKET=lessonlines-exports
STRIPE_SECRET_KEY=sk_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### Frontend
```
VITE_API_URL=https://api.lessonlines.com
VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxx
VITE_COGNITO_APP_CLIENT_ID=xxxxx
VITE_STRIPE_PUBLISHABLE_KEY=pk_xxxxx
```

## Notes for Implementation

- Use SQLAlchemy with async support (asyncpg) for better Lambda performance
- RDS Proxy is essential—without it, Lambda will exhaust database connections
- Start with 3 topics: Civil War, American Revolution, WWII
- Start with 2-3 curriculum frameworks: Common Core (national), AP US History, one state standard (e.g., Texas TEKS)
- Events should be aligned to multiple standards where appropriate
- PDF export can be Phase 5—it's the pro feature, not MVP
- Keep the UI close to the mockup (see timeline_ui_mockup.html)
- Mobile responsiveness is nice-to-have for v1, not required
- Focus on the core loop: search events → filter by standard → drag to timeline → save → export
- Consider adding a "standards coverage" view in future that shows which standards a timeline addresses
- Full-text search in PostgreSQL (using `to_tsvector`) is sufficient for event search; no need for Elasticsearch initially
