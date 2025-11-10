from django.db import connection

schemas = ['public', 'kk_company', 'osm_company']

for schema in schemas:
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = '{schema}'
        AND tablename LIKE 'training%'
        ORDER BY tablename
    """)
    tables = cursor.fetchall()

    print(f"\n{schema} schema:")
    print(f"  Training tables found: {len(tables)}")

    if tables:
        for table in tables:
            print(f"    - {table[0]}")
    else:
        print("    (no training tables)")
