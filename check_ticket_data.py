#!/usr/bin/env python3
"""
Check ticket data in database
"""

from app import app, db, Ticket, Message

def check_ticket_data():
    with app.app_context():
        print("=== CHECKING TICKET DATA ===\n")
        
        # Check total tickets
        total_tickets = db.session.query(Ticket).count()
        print(f"Total tickets: {total_tickets}")
        
        # Check ticket statuses
        statuses = db.session.query(Ticket.Status, db.func.count(Ticket.TicketID)).group_by(Ticket.Status).all()
        print(f"\nTicket statuses:")
        for status, count in statuses:
            print(f"  {status}: {count}")
        
        # Check priorities
        priorities = db.session.query(Ticket.Priority, db.func.count(Ticket.TicketID)).group_by(Ticket.Priority).all()
        print(f"\nTicket priorities:")
        for priority, count in priorities:
            print(f"  {priority}: {count}")
        
        # Check recent tickets
        recent_tickets = db.session.query(Ticket).order_by(Ticket.CreatedAt.desc()).limit(5).all()
        print(f"\nRecent tickets:")
        for ticket in recent_tickets:
            print(f"  ID: {ticket.TicketID}, Status: {ticket.Status}, Priority: {ticket.Priority}, Created: {ticket.CreatedAt}")
        
        # Check what should be "active" tickets
        active_statuses = ['open', 'in_progress', 'pending', 'new']
        for status in active_statuses:
            count = db.session.query(Ticket).filter(Ticket.Status == status).count()
            print(f"\nTickets with status '{status}': {count}")
        
        # Check messages
        total_messages = db.session.query(Message).count()
        print(f"\nTotal messages: {total_messages}")
        
        # Check bot messages
        bot_messages = db.session.query(Message).filter(Message.IsFromBot == True).count()
        print(f"Bot messages: {bot_messages}")

if __name__ == "__main__":
    check_ticket_data()
