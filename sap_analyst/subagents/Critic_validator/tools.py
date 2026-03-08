"""
Tools for the SAP Analyst agent.
Each tool mimics querying an SAP HANA-like schema via BigQuery.
"""

from google.adk.tools import FunctionTool


def query_sap_table(table_name: str, filters: dict = None) -> dict:
    """
    Query a mock SAP table (e.g., MARA, EKPO, EKKO) and return results.

    Args:
        table_name: SAP table name (e.g., 'MARA', 'EKPO', 'EKKO')
        filters: Optional key-value filters (e.g., {'MATNR': '000000000000001234'})

    Returns:
        dict with 'columns' and 'rows' keys.
    """
    # Mock data — replace with actual BigQuery client calls
    mock_data = {
        "MARA": {
            "columns": ["MATNR", "MAKTX", "MEINS", "MTART"],
            "rows": [
                ["000000000000001234", "Pump Assembly XL", "EA", "FERT"],
                ["000000000000005678", "Steel Rod 10mm", "KG", "ROH"],
            ],
        },
        "EKKO": {
            "columns": ["EBELN", "LIFNR", "BEDAT", "WAERS"],
            "rows": [
                ["4500000001", "VENDOR_001", "2026-01-15", "USD"],
                ["4500000002", "VENDOR_002", "2026-02-01", "EUR"],
            ],
        },
        "EKPO": {
            "columns": ["EBELN", "EBELP", "MATNR", "MENGE", "NETPR"],
            "rows": [
                ["4500000001", "00010", "000000000000001234", 10.0, 250.00],
                ["4500000002", "00010", "000000000000005678", 500.0, 1.50],
            ],
        },
    }

    table = table_name.upper()
    if table not in mock_data:
        return {"error": f"Table '{table}' not found in mock schema."}

    result = mock_data[table]

    if filters:
        col_idx = {col: i for i, col in enumerate(result["columns"])}
        filtered_rows = [
            row for row in result["rows"]
            if all(
                str(row[col_idx[k]]) == str(v)
                for k, v in filters.items()
                if k in col_idx
            )
        ]
        result = {"columns": result["columns"], "rows": filtered_rows}

    return result


def get_table_schema(table_name: str) -> dict:
    """
    Return the schema (field descriptions) for an SAP table.

    Args:
        table_name: SAP table name (e.g., 'MARA', 'EKPO')

    Returns:
        dict with field names and descriptions.
    """
    schemas = {
        "MARA": {
            "description": "General Material Data",
            "fields": {
                "MATNR": "Material Number",
                "MAKTX": "Material Description",
                "MEINS": "Base Unit of Measure",
                "MTART": "Material Type (e.g., FERT=Finished, ROH=Raw)",
            },
        },
        "EKKO": {
            "description": "Purchasing Document Header",
            "fields": {
                "EBELN": "Purchase Order Number",
                "LIFNR": "Vendor Account Number",
                "BEDAT": "Purchase Order Date",
                "WAERS": "Currency Key",
            },
        },
        "EKPO": {
            "description": "Purchasing Document Item",
            "fields": {
                "EBELN": "Purchase Order Number",
                "EBELP": "Item Number",
                "MATNR": "Material Number",
                "MENGE": "Purchase Order Quantity",
                "NETPR": "Net Price",
            },
        },
    }

    table = table_name.upper()
    if table not in schemas:
        return {"error": f"Schema for '{table}' not found."}
    return schemas[table]


# Wrap as ADK FunctionTools
query_tool = FunctionTool(query_sap_table)
schema_tool = FunctionTool(get_table_schema)
