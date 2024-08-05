training_week_html_base = """
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background-color: #be5e5b;
            color: #ffffff;
            text-align: center;
            padding: 20px;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .content {
            padding: 20px;
        }
        .content h2 {
            color: #be5e5b;
            font-size: 20px;
            margin-bottom: 10px;
        }
        .content ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        .content li {
            background-color: #f9f9f9;
            margin-bottom: 10px;
            padding: 15px;
            border-left: 5px solid #be5e5b;
            border-radius: 5px;
            color: #333;
        }
        .content li strong {
            display: block;
            font-size: 16px;
            margin-bottom: 5px;
            color: #333;
        }
        .footer {
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px;
            font-size: 9px;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Training Schedule</h1>
        </div>
        <div class="content">
            <h2>Get pumped for this week's training.</h2>
            <ul>
"""
