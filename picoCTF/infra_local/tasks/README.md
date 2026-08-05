# Ansible Task Lists

Minimal task lists that are custom to bootstrapping a local infrastructure.

In general we strive to integrate any tasks into a standardized `ansible` role,
so that any deployment environment can benefit from the automation. However in
some limited cases, such as on bootstrapping or event specific tasks, it makes
sense to isolate the changes with the specific deployment. This approach should
be used sparingly.
