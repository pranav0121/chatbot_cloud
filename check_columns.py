from app import app, db
from sqlalchemy import text

with app.app_context():
    result = db.session.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'sla_logs' ORDER BY ORDINAL_POSITION"))
    print('SLA_LOGS columns:')
    for row in result:
        print(f'  {row[0]}')
