CREATE TABLE IF NOT EXISTS points (
                                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      user_id INTEGER NOT NULL,
                                      user_display_name VARCHAR(255) NOT NULL,
                                      server_id INTEGER NOT NULL,
                                      points INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS administrators (
    user_id INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS history (
                                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                                       user_id INTEGER NOT NULL,
                                       user_display_name VARCHAR(255) NOT NULL,
                                       server_id INTEGER NOT NULL,
                                       points_delta INTEGER NOT NULL,
                                       previous_value INTEGER NOT NULL,
                                       modifier_id INTEGER NOT NULL,
                                       modifier_display_name VARCHAR(255) NOT NULL,
                                       timestamp DATETIME NOT NULL -- Please store in UTC, not localtime
);