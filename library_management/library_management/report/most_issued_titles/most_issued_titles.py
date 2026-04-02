import frappe


def execute(filters=None):
    columns = [
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Issue Count", "fieldname": "issue_count", "fieldtype": "Int", "width": 120},
    ]
    data = frappe.db.sql(
        """
        select item, count(*) as issue_count
        from `tabLibrary Transaction`
        where transaction_type = 'Issue'
        group by item
        order by issue_count desc, item asc
        """,
        as_dict=True,
    )
    return columns, data
