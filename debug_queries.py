#!/usr/bin/env python3
"""
Debug dashboard metrics queries
"""

from app import app, db, Ticket, Message
from datetime import datetime, timedelta
from sqlalchemy import func

def debug_queries():
    with app.app_context():
        print("=== DEBUGGING DASHBOARD QUERIES ===\n")
        
        # Test the active tickets query
        print("1. Testing active tickets query:")
        active_tickets_query = db.session.query(Ticket).filter(
            Ticket.Status.in_(['open', 'in_progress'])
        )
        print(f"   SQL: {active_tickets_query}")
        active_tickets = active_tickets_query.count()
        print(f"   Result: {active_tickets}")
        
        # Test with different status variations
        print("\n2. Testing different status queries:")
        statuses_to_test = [
            ['open', 'in_progress'],
            ['Open', 'In_Progress'],
            ['OPEN', 'IN_PROGRESS'],
            ['open'],
            ['in_progress']
        ]
        
        for status_list in statuses_to_test:
            count = db.session.query(Ticket).filter(Ticket.Status.in_(status_list)).count()
            print(f"   Status {status_list}: {count}")
        
        # Check actual status values in database
        print("\n3. Actual status values in database:")
        statuses = db.session.query(Ticket.Status, func.count(Ticket.TicketID)).group_by(Ticket.Status).all()
        for status, count in statuses:
            print(f"   '{status}': {count}")
        
        # Test escalation query
        print("\n4. Testing escalation query:")
        tickets = db.session.query(Ticket).filter(
            Ticket.Status.in_(['open', 'in_progress'])
        ).order_by(Ticket.Priority.desc(), Ticket.CreatedAt.desc()).all()
        print(f"   Found {len(tickets)} tickets for escalation")
        
        # Test bot interactions query
        print("\n5. Testing bot interactions query:")
        last_24h = datetime.utcnow() - timedelta(hours=24)
        print(f"   Looking for messages since: {last_24h}")
        
        total_messages_24h = db.session.query(func.count(Message.MessageID)).filter(
            Message.CreatedAt >= last_24h
        ).scalar()
        print(f"   Total messages in last 24h: {total_messages_24h}")
        
        bot_messages_24h = db.session.query(func.count(Message.MessageID)).filter(
            Message.CreatedAt >= last_24h,
            Message.IsBotResponse == True
        ).scalar()
        print(f"   Bot messages in last 24h: {bot_messages_24h}")
        
        # Check all bot messages ever
        all_bot_messages = db.session.query(func.count(Message.MessageID)).filter(
            Message.IsBotResponse == True
        ).scalar()
        print(f"   Total bot messages ever: {all_bot_messages}")

if __name__ == "__main__":
    debug_queries()
