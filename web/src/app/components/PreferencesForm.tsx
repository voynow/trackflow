import React from 'react';
import { Day, Preferences, SessionType } from '../types';

type PreferencesFormProps = {
    preferences: Preferences;
    setPreferences: React.Dispatch<React.SetStateAction<Preferences>>;
    onSave: () => Promise<void>;
    onCancel: () => void;
    isSaving: boolean;
};

export function PreferencesForm({
    preferences,
    setPreferences,
    onSave,
    onCancel,
    isSaving
}: PreferencesFormProps): JSX.Element {
    const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
        e.preventDefault();
        onSave();
    };

    const updateIdealTrainingWeek = (day: Day, sessionType: SessionType | null): void => {
        const updatedWeek = preferences.ideal_training_week?.filter(session => session.day !== day) || [];
        if (sessionType) {
            updatedWeek.push({ day, session_type: sessionType });
        }
        setPreferences({ ...preferences, ideal_training_week: updatedWeek });
    };

    const days: Day[] = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'];
    const sessionTypes: SessionType[] = ['easy run', 'long run', 'speed workout', 'rest day', 'moderate run'];

    return (
        <form onSubmit={handleSubmit} className="bg-gray-50 p-6 max-w-3xl mx-auto text-gray-800 rounded-3xl">

            <div className="mb-8">
                <label className="block text-sm font-medium mb-2 text-gray-600">Race Distance</label>
                <select
                    value={preferences.race_distance || ''}
                    onChange={(e) => setPreferences({ ...preferences, race_distance: e.target.value as Preferences['race_distance'] })}
                    className="w-full bg-gray-50 rounded-xl py-3 px-4 text-gray-800 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300"
                >
                    <option value="">Select distance</option>
                    <option value="5k">5K</option>
                    <option value="10k">10K</option>
                    <option value="half marathon">Half Marathon</option>
                    <option value="marathon">Marathon</option>
                    <option value="ultra marathon">Ultra Marathon</option>
                    <option value="none">None</option>
                </select>
            </div>

            <div className="mb-8">
                <label className="block text-sm font-medium mb-4 text-gray-600">Ideal Training Week</label>
                <div className="space-y-2">
                    {days.map((day) => {
                        const sessionType = preferences.ideal_training_week?.find(session => session.day === day)?.session_type;
                        const isPreferenceSet = !!sessionType;
                        return (
                            <div key={day} className={`flex items-center border rounded-xl overflow-hidden border-gray-300`}>
                                <span className={`w-20 font-medium px-4 py-3 bg-gray-50 ${isPreferenceSet ? 'text-gray-600' : 'text-gray-300'}`}>
                                    {day}
                                </span>
                                <select
                                    value={sessionType || ''}
                                    onChange={(e) => updateIdealTrainingWeek(day, e.target.value as SessionType || null)}
                                    className={`flex-grow py-3 px-4 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-300 ${isPreferenceSet ? 'text-gray-800' : 'text-gray-300'}`}
                                >
                                    <option value="">No Preference</option>
                                    {sessionTypes.map((type) => (
                                        <option key={type} value={type}>{type}</option>
                                    ))}
                                </select>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="flex justify-end space-x-4">
                <button
                    type="button"
                    onClick={onCancel}
                    className="px-4 py-2 bg-gray-700 text-white rounded-xl hover:bg-gray-500 transition duration-300 ease-in-out"
                    disabled={isSaving}
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    className="px-4 py-2 bg-blue-400 text-white rounded-xl hover:bg-blue-300 transition duration-300 ease-in-out relative"
                    disabled={isSaving}
                >
                    {isSaving ? (
                        <>
                            <span className="opacity-0">Save</span>
                            <span className="absolute inset-0 flex items-center justify-center">
                                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            </span>
                        </>
                    ) : (
                        'Save'
                    )}
                </button>
            </div>
        </form>
    );
}