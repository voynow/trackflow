from src.types.training_week import (
    Day,
    SessionType,
    TrainingSession,
    TrainingWeek,
)


def standardize_training_week(
    training_week: TrainingWeek,
) -> TrainingWeek:
    """
    Sort the training week by day of the week and add missing days as rest days
    """
    day_order = list(Day)
    existing_days = set(session.day for session in training_week.sessions)

    # Add missing days as rest days
    for day in day_order:
        if day not in existing_days:
            training_week.sessions.append(
                TrainingSession(
                    day=day,
                    session_type=SessionType.REST,
                    distance=0.0,
                    notes="Rest day, take it easy!",
                    completed=False,
                )
            )

    # Sort the completed training week
    return TrainingWeek(
        sessions=sorted(training_week.sessions, key=lambda x: day_order.index(x.day))
    )

