export type ProfileData = {
    firstname: string;
    lastname: string;
    email: string;
    preferences?: string;
    profile: string;
    is_active: boolean;
};

export type Preferences = {
    race_distance?: 'FIVE_KILOMETER' | 'TEN_KILOMETER' | 'HALF_MARATHON' | 'MARATHON' | 'ULTRA';
    long_run_day?: 'Mon' | 'Tues' | 'Wed' | 'Thurs' | 'Fri' | 'Sat' | 'Sun';
    speed_workout_day?: 'Mon' | 'Tues' | 'Wed' | 'Thurs' | 'Fri' | 'Sat' | 'Sun';
    n_days_per_week?: number;
    unavailable_days?: Array<'Mon' | 'Tues' | 'Wed' | 'Thurs' | 'Fri' | 'Sat' | 'Sun'>;
};
