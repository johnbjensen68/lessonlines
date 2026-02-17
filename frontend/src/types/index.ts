// User types
export interface User {
  id: string;
  email: string;
  display_name: string | null;
  is_pro: boolean;
  pro_purchased_at: string | null;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

// Topic types
export interface Topic {
  id: string;
  slug: string;
  name: string;
  description: string | null;
}

// Tag types
export interface Tag {
  id: string;
  name: string;
  category: string | null;
}

// Standard types
export interface StandardBrief {
  id: string;
  code: string;
  title: string;
  framework_code: string;
  grade_level: string | null;
}

// Event types
export interface EventListItem {
  id: string;
  title: string;
  description: string;
  date_display: string;
  location: string | null;
  image_url: string | null;
  tags: Tag[];
}

export interface Event extends EventListItem {
  topic_id: string;
  date_start: string;
  date_end: string | null;
  date_precision: string;
  significance: string | null;
  source_url: string | null;
  source_citation: string | null;
  image_url: string | null;
  standards: StandardBrief[];
  created_at: string;
}

// Timeline types
export interface TimelineEvent {
  id: string;
  timeline_id: string;
  event_id: string | null;
  position: number;
  custom_title: string | null;
  custom_description: string | null;
  custom_date_display: string | null;
  custom_date_start: string | null;
  event: EventListItem | null;
}

export interface Timeline {
  id: string;
  user_id: string;
  title: string;
  subtitle: string | null;
  color_scheme: string;
  layout: string;
  font: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  events: TimelineEvent[];
}

export interface TimelineCreate {
  title: string;
  subtitle?: string;
  color_scheme?: string;
  layout?: string;
  font?: string;
}

export interface TimelineUpdate {
  title?: string;
  subtitle?: string;
  color_scheme?: string;
  layout?: string;
  font?: string;
}

export interface TimelineEventCreate {
  event_id?: string;
  custom_title?: string;
  custom_description?: string;
  custom_date_display?: string;
  custom_date_start?: string;
}

// API types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
