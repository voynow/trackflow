import React from 'react';
import { Preferences } from '../types';

type PreferencesFormProps = {
    preferences: Preferences;
    setPreferences: React.Dispatch<React.SetStateAction<Preferences>>;
    onSave: () => Promise<void>;
    onCancel: () => void;
};

export function PreferencesForm({
    preferences,
    setPreferences,
    onSave,
    onCancel
}: PreferencesFormProps): JSX.Element {
    const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
        e.preventDefault();
        onSave();
    };

    return (
        <form onSubmit={handleSubmit}>
            {/* Race Distance */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Race Distance</label>
                <select
                    value={preferences.race_distance || ''}
                    onChange={(e) => setPreferences({ ...preferences, race_distance: e.target.value as Preferences['race_distance'] })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                >
                    <option value="">Select distance</option>
                    <option value="FIVE_KILOMETER">5K</option>
                    <option value="TEN_KILOMETER">10K</option>
                    <option value="HALF_MARATHON">Half Marathon</option>
                    <option value="MARATHON">Marathon</option>
                    <option value="ULTRA">Ultra Marathon</option>
                </select>
            </div>

            {/* Long Run Day */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Long Run Day</label>
                <select
                    value={preferences.long_run_day || ''}
                    onChange={(e) => setPreferences({ ...preferences, long_run_day: e.target.value as Preferences['long_run_day'] })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                >
                    <option value="">Select day</option>
                    {['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'].map((day) => (
                        <option key={day} value={day}>{day}</option>
                    ))}
                </select>
            </div>

            {/* Speed Workout Day */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Speed Workout Day</label>
                <select
                    value={preferences.speed_workout_day || ''}
                    onChange={(e) => setPreferences({ ...preferences, speed_workout_day: e.target.value as Preferences['speed_workout_day'] })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                >
                    <option value="">Select day</option>
                    {['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'].map((day) => (
                        <option key={day} value={day}>{day}</option>
                    ))}
                </select>
            </div>

            {/* Number of Days per Week */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Days per Week</label>
                <input
                    type="number"
                    min="1"
                    max="7"
                    value={preferences.n_days_per_week || ''}
                    onChange={(e) => setPreferences({ ...preferences, n_days_per_week: parseInt(e.target.value) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                />
            </div>

            {/* Unavailable Days */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Unavailable Days</label>
                {(['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'] as const).map((day) => (
                    <label key={day} className="inline-flex items-center mt-1 mr-4">
                        <input
                            type="checkbox"
                            checked={preferences.unavailable_days?.includes(day) ?? false}
                            onChange={(e) => {
                                const updatedDays = e.target.checked
                                    ? [...(preferences.unavailable_days || []), day]
                                    : (preferences.unavailable_days || []).filter(d => d !== day);
                                setPreferences({ ...preferences, unavailable_days: updatedDays as Preferences['unavailable_days'] });
                            }}
                            className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                        />
                        <span className="ml-2 text-sm text-gray-700">{day}</span>
                    </label>
                ))}
            </div>

            <div className="flex justify-end space-x-2">
                <button
                    type="button"
                    onClick={onCancel}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition"
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                >
                    Save
                </button>
            </div>
        </form>
    );
}