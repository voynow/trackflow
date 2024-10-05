export type ProfileData = {
    firstname: string;
    lastname: string;
    email: string;
    preferences?: string;
    profile: string;
    is_active: boolean;
};

export type Day = 'Mon' | 'Tues' | 'Wed' | 'Thurs' | 'Fri' | 'Sat' | 'Sun';
export type SessionType = 'easy run' | 'long run' | 'speed workout' | 'rest day' | 'moderate run';

export type Preferences = {
    race_distance?: '5k' | '10k' | 'half marathon' | 'marathon' | 'ultra marathon' | null;
    ideal_training_week?: Array<{
        day: Day;
        session_type: SessionType;
    }>;
};
