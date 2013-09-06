from tools.mongo import db


__info__ = """
Task:
    commit:
        description
        hash
        branch
        author
    project
    status: const.STATUSES
    created
    violations: [
        name
        status: const.STATUSES
        raw
        prepared
        preview
        plot: {
            'name': value
        }
    ]
"""
Tasks = db.tasks
