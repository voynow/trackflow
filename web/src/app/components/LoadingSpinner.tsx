
type LoadingSpinnerProps = {
    error: string | null;
};

export function LoadingSpinner({ error }: LoadingSpinnerProps): JSX.Element {
    if (error) {
        return (
            <div className="text-center">
                <p className="text-red-500 mb-4">{error}</p>
                <p className="text-sm text-gray-600">
                    If the issue persists, please contact support.
                </p>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center space-y-4">
            <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse delay-75"></div>
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse delay-150"></div>
                <span className="text-sm text-gray-500 ml-2">Loading...</span>
            </div>
        </div>
    );
}