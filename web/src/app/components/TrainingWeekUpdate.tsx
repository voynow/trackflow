import React from 'react';

interface DisplaySession {
    day: string;
    session_type: string;
    distance: number;
    notes: string;
}

interface TrainingWeekUpdateProps {
    data: {
        mid_week_analysis: {
            activities: any[];
            miles_ran: number;
            miles_target: number;
        };
        training_week_update_with_planning: {
            training_week: DisplaySession[];
        };
    };
}

const TrainingWeekUpdate: React.FC<TrainingWeekUpdateProps> = ({ data }) => {
    const { mid_week_analysis, training_week_update_with_planning } = data;

    const completedSessions = mid_week_analysis.activities.map((activity: any) => ({
        day: new Date(activity.date).toLocaleDateString('en-US', { weekday: 'short' }),
        session_type: 'completed',
        distance: activity.distance_in_miles,
        notes: `Pace: ${activity.pace_minutes_per_mile} min/mile, Elevation: ${activity.elevation_gain_in_feet} feet`,
    }));

    const upcomingSessions = training_week_update_with_planning.training_week;

    const progress_percentage = mid_week_analysis.miles_target > 0
        ? (mid_week_analysis.miles_ran / mid_week_analysis.miles_target) * 100
        : 0;

    return (
        <div className="bg-white shadow-md rounded-lg p-6 w-full max-w-2xl">
            <h2 className="text-2xl font-bold mb-4">Updated Training Schedule</h2>
            <ul className="space-y-4">
                {[...completedSessions, ...upcomingSessions].map((session, index) => (
                    <li key={index} className={`p-4 rounded-md ${session.session_type === 'completed' ? 'bg-green-100' : 'bg-blue-100'}`}>
                        <strong>{session.day}</strong> <span>{session.distance} miles</span>
                        <br />
                        <span>{session.notes}</span>
                    </li>
                ))}
            </ul>
            <div className="mt-6 bg-gray-200 p-4 rounded-md">
                <span className="font-bold">Completed {Math.round(mid_week_analysis.miles_ran)} of {Math.round(mid_week_analysis.miles_target)} miles</span>
                <div className="w-full bg-gray-300 rounded-full h-2.5 mt-2">
                    <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${Math.round(progress_percentage)}%` }}></div>
                </div>
            </div>
        </div>
    );
};

export default TrainingWeekUpdate;
