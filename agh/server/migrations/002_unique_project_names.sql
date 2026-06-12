-- Project names are exact human-readable identifiers, so they must be unique globally.

CREATE UNIQUE INDEX IF NOT EXISTS ux_projects_name
    ON projects(name);
