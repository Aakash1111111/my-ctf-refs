# Fetched Artifacts

These directories contain artifacts fetched from the remote hosts to allow
synchronization and coordination.

By default files in the following directories are ignored by git:
- `certs`
- `keys`

You should not need to edit or directly interact with these files. If they are
removed the ansible automation will simply fetch them when next run.
