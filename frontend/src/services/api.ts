import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000';

// API Client instance
export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // CrewAI can take time
});

// Types for /recommend (Fast Engine)
export interface Traveler {
  name: string;
  age: number;
  food_preference: string;
  mood: string;
  travel_purpose: string;
  medical_conditions: string[];
  activity_level: 'low' | 'medium' | 'high';
  budget_preference: 'budget' | 'standard' | 'luxury';
}

export interface GroupTripRequest {
  travelers: Traveler[];
  budget: number;
  days: number;
  preferred_vibe: string;
  priorities: string[];
  destination_preference?: string | null;
  expectations?: string;
}

export interface ExpectationMatchResponse {
  match_percentage: number;
  summary: string;
}

export interface RecommendationDetails {
  destination: string;
  compatibility_score: number;
  reasons: string[];
  warnings: string[];
  top_activities: string[];
  expectation_match: ExpectationMatchResponse;
  factor_scores: Record<string, number>;
  score_explanation: string;
}

// Types for /recommendation/ (Deep CrewAI Engine)
export interface TravelerProfile {
  name: string;
  age: number;
  medical_conditions: string[];
  vibe_preference: string;
  accommodation_preference: string;
  travel_style: string;
  travel_purpose: string;
}

export interface TravelGroupRequest {
  travelers: TravelerProfile[];
  total_budget: number;
  num_days: number;
  expectations: string;
  destination_preference?: string | null;
}

export interface BudgetAllocation {
  accommodation_cost: number;
  activities_cost: number;
  buffer_amount: number;
  remaining_balance: number;
  explanation: string;
}

export interface MatchScoreDetail {
  score: number;
  matching_aspects: string[];
  deviating_aspects: string[];
  reality_check_summary: string;
}

export interface WeatherSafetyDetail {
  general_condition: string;
  health_warnings: string[];
  alternative_indoor_activities: string[];
}

export interface ItineraryActivity {
  time: string;
  activity_name: string;
  description: string;
  estimated_cost: number;
  fatigue_level: number;
  assigned_to: string[];
}

export interface ItineraryDay {
  day: number;
  activities: ItineraryActivity[];
}

export interface CrewRecommendationResponse {
  destination_name: string;
  description: string;
  group_compatibility_score: number;
  group_itinerary: ItineraryDay[];
  solo_itineraries: Record<string, ItineraryDay[]>;
  reunion_schedule: ItineraryDay[];
  conflict_resolution_summary: string;
  budget_analysis: BudgetAllocation;
  weather_health_safety: WeatherSafetyDetail;
  expectation_reality_match: MatchScoreDetail;
  explainable_ai_reasons: string[];
  smart_budget_expansions: string[];
}

// API Functions
export const ApiService = {
  // Test connection
  async testConnection(): Promise<boolean> {
    try {
      const response = await apiClient.get('/');
      return response.status === 200;
    } catch (e) {
      console.warn('API connection test failed:', e);
      return false;
    }
  },

  // Get available destinations list
  async getDestinations(): Promise<string[]> {
    try {
      const response = await apiClient.get<string[]>('/recommendation/destinations');
      return response.data;
    } catch (e) {
      console.error('Failed to fetch destinations:', e);
      // Fallback local list of destinations
      return ['Goa', 'Srinagar', 'Jaipur', 'Bangalore'];
    }
  },

  // Get Fast Recommendation list
  async getFastRecommendations(request: GroupTripRequest): Promise<RecommendationDetails[]> {
    const response = await apiClient.post<RecommendationDetails[]>('/recommend', request);
    return response.data;
  },

  // Get Deep CrewAI Recommendation
  async getCrewRecommendations(request: TravelGroupRequest): Promise<CrewRecommendationResponse> {
    // Note FastAPI route recommendation.router defines POST /recommendation/ with prefix /recommendation
    const response = await apiClient.post<CrewRecommendationResponse>('/recommendation/', request);
    return response.data;
  },
};
