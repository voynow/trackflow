import React from 'react';

interface TrainingSession {
    id: string;
    day: string;
    session_type: string;
    distance: number;
    notes: string;
    completed: boolean;
}

export interface TrainingWeekProps {
    data: {
        training_week: {
            sessions: TrainingSession[];
        };
    };
}


const TrainingWeek: React.FC<TrainingWeekProps> = ({ data }) => {
    if (!data?.training_week?.sessions) {
        return <div className="flex items-center justify-center h-screen text-xl text-gray-500">No training data available.</div>;
    }

    const { sessions } = data.training_week;
    const totalMileage = sessions.reduce((total, session) => total + session.distance, 0);
    const completedMileage = sessions.reduce((total, session) => session.completed ? total + session.distance : total, 0);
    const progressPercentage = totalMileage > 0 ? Math.round((completedMileage / totalMileage) * 100) : 0;

    const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const sessionsByDay = daysOfWeek.map(day =>
        sessions.find(session => session.day.toLowerCase().startsWith(day.toLowerCase())) || null
    );

    return (
        <div className="w-full lg:w-3/4 xl:w-1/2 p-8">
            <div className="bg-white rounded-3xl">
                <div className="p-4">

                    <div className="bg-gray-900 text-white rounded-2xl p-6">
                        <h2 className="text-2xl font-light mb-4">Weekly Progress</h2>
                        <div className="flex items-center justify-between mb-4">
                            <div className="text-6xl font-bold">{progressPercentage}%</div>
                            <div className="text-gray-400">{completedMileage} of {totalMileage} miles completed</div>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-3">
                            <div
                                className="bg-gradient-to-r from-blue-400 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                                style={{ width: `${progressPercentage}%` }}
                            ></div>
                        </div>
                    </div>
                </div>
                <div className="grid grid-cols-1 gap-2 p-8">
                    <div className="grid grid-cols-1 gap-4 mb-8">
                        {daysOfWeek.map((day, index) => (
                            <div key={day} className="bg-gray-50 rounded-xl p-4 shadow-md transition-all duration-300 hover:shadow-lg flex items-start min-h-[120px]">
                                <div className="w-20 text-lg font-medium text-gray-500">{day}</div>
                                {sessionsByDay[index] ? (
                                    <div className="flex-grow flex flex-col justify-between h-full">
                                        <div className="flex items-center justify-between w-full">
                                            <div>
                                                <div className="text-2xl font-bold">{sessionsByDay[index]?.distance} mi</div>
                                                <div className="text-sm text-gray-600">{sessionsByDay[index]?.session_type}</div>
                                            </div>
                                            <div className={`w-4 h-4 rounded-full ${sessionsByDay[index]?.completed ? 'bg-green-400' : 'bg-gray-300'}`}></div>
                                        </div>
                                        {sessionsByDay[index]?.notes && (
                                            <div className="text-xs text-gray-500 mt-2 italic">{sessionsByDay[index]?.notes}</div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="text-lg font-medium text-gray-400">Rest</div>
                                )}
                            </div>
                        ))}
                    </div>

                </div>
            </div>
        </div>
    );
};

export default TrainingWeek;
