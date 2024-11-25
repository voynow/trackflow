resource "aws_cloudwatch_event_connection" "trackflow_api_connection" {
  name               = "trackflow-api-connection"
  authorization_type = "API_KEY"

  auth_parameters {
    api_key {
      key   = "x-api-key"
      value = var.api_key
    }
  }
}

resource "aws_cloudwatch_event_api_destination" "trackflow_daily_destination" {
  name                             = "trackflow-daily-destination"
  connection_arn                   = aws_cloudwatch_event_connection.trackflow_api_connection.arn
  http_method                      = "POST"
  invocation_endpoint             = "${var.api_base_url}/update-all-users/"
  invocation_rate_limit_per_second = 1
}

resource "aws_cloudwatch_event_rule" "trackflow_daily" {
  name                = "trackflow-daily"
  description         = "Trigger daily TrackFlow updates at 11:00 AM EST"
  schedule_expression = "cron(0 16 * * ? *)"
}

resource "aws_iam_role" "eventbridge_api_destination" {
  name = "trackflow-daily-eventbridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge_api_destination" {
  name = "trackflow-daily-eventbridge-policy"
  role = aws_iam_role.eventbridge_api_destination.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "events:InvokeApiDestination"
        ]
        Resource = [
          aws_cloudwatch_event_api_destination.trackflow_daily_destination.arn
        ]
      }
    ]
  })
}

resource "aws_cloudwatch_event_target" "trackflow_daily_target" {
  rule      = aws_cloudwatch_event_rule.trackflow_daily.name
  target_id = "TrackflowDailyTarget"
  arn       = aws_cloudwatch_event_api_destination.trackflow_daily_destination.arn
  role_arn  = aws_iam_role.eventbridge_api_destination.arn
} 