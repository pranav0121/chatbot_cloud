#!/usr/bin/env python3
"""
Enhanced SLA Monitor - Robust version that handles all edge cases gracefully
"""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import time

logger = logging.getLogger(__name__)


class EnhancedSLAMonitor:
    """Enhanced SLA Monitor that handles all edge cases and data quality issues"""

    def __init__(self, app=None):
        self.app = app
        self.monitoring = False
        self.check_interval = 300  # Check every 5 minutes
        self.monitor_thread = None

    def start_monitoring(self):
        """Start the SLA monitoring service"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Enhanced SLA monitoring service started")

    def stop_monitoring(self):
        """Stop the SLA monitoring service"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        logger.info("Enhanced SLA monitoring service stopped")

    def _monitor_loop(self):
        """Main monitoring loop with enhanced error handling"""
        while self.monitoring:
            try:
                with self.app.app_context():
                    if self._tables_exist():
                        # Check SLA compliance with enhanced error handling
                        self._check_sla_compliance_enhanced()
                        # Process escalations with enhanced error handling
                        self._process_escalations_enhanced()
                        # Auto-escalate tickets with enhanced error handling
                        self._check_and_auto_escalate_tickets_enhanced()
                    else:
                        logger.debug(
                            "SLA monitoring waiting for database tables to be created...")

                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in enhanced SLA monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

    def _tables_exist(self):
        """Check if required tables exist"""
        try:
            from app import db
            from sqlalchemy import text

            # Check if the required tables and columns exist
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME IN ('sla_logs', 'partners', 'bot_configurations', 'Tickets')
            """))

            table_count = result.scalar()
            return table_count >= 4

        except Exception as e:
            logger.debug(f"Error checking table existence: {e}")
            return False

    def _check_sla_compliance_enhanced(self):
        """Enhanced SLA compliance check with robust error handling"""
        try:
            from app import db, Ticket
            from database import SLALog, EscalationRule

            # Get all active tickets with proper error handling
            try:
                active_tickets = Ticket.query.filter(
                    Ticket.Status.in_(['open', 'in_progress', 'escalated'])
                ).all()
            except Exception as e:
                logger.warning(f"Could not query active tickets: {e}")
                return

            for ticket in active_tickets:
                try:
                    # Ensure ticket has required attributes
                    if not hasattr(ticket, 'TicketID') or not ticket.TicketID:
                        logger.warning(f"Skipping ticket with no ID: {ticket}")
                        continue

                    # Get or create SLA log for this ticket
                    sla_log = SLALog.query.filter_by(
                        ticket_id=ticket.TicketID).first()

                    if not sla_log:
                        # Create initial SLA log with validation
                        sla_log = self._create_initial_sla_log_enhanced(ticket)
                        if not sla_log:
                            continue

                    # Check if SLA log has required data
                    if not sla_log.created_at or not sla_log.sla_target_hours:
                        logger.warning(
                            f"SLA log {sla_log.id} missing required data, skipping")
                        continue

                    # Check if SLA is breached with enhanced validation
                    if sla_log and not sla_log.is_breached:
                        self._check_sla_breach_enhanced(sla_log)

                except Exception as e:
                    logger.warning(
                        f"Error processing ticket {getattr(ticket, 'TicketID', 'unknown')}: {e}")
                    continue

            db.session.commit()

        except Exception as e:
            logger.error(f"Error in enhanced SLA compliance check: {e}")

    def _create_initial_sla_log_enhanced(self, ticket):
        """Create initial SLA log with enhanced validation"""
        try:
            from app import db
            from database import SLALog, EscalationRule

            # Validate ticket data
            if not hasattr(ticket, 'Priority') or not hasattr(ticket, 'CreatedAt'):
                logger.warning(
                    f"Ticket {ticket.TicketID} missing required fields for SLA log creation")
                return None

            # Get escalation rule for this ticket with fallback
            escalation_rule = None
            if ticket.Priority:
                try:
                    escalation_rule = EscalationRule.query.filter_by(
                        priority=ticket.Priority.lower(),
                        is_active=True
                    ).first()
                except Exception as e:
                    logger.debug(f"Could not query escalation rules: {e}")

            # Determine SLA hours with robust fallback
            if escalation_rule and escalation_rule.level_1_sla_hours:
                sla_hours = escalation_rule.level_1_sla_hours
            else:
                # Use default SLA times based on priority
                priority_defaults = {
                    'critical': 1.0,
                    'high': 4.0,
                    'medium': 8.0,
                    'low': 24.0
                }
                priority_key = ticket.Priority.lower() if ticket.Priority else 'medium'
                sla_hours = priority_defaults.get(priority_key, 8.0)

            # Get escalation level with fallback
            escalation_level = getattr(ticket, 'escalation_level', 0) or 0

            # Map escalation level to name
            level_names = {0: 'Bot', 1: 'ICP', 2: 'YouCloud'}
            level_name = level_names.get(escalation_level, 'Bot')

            # Create SLA log with proper timestamps
            current_time = datetime.now()
            created_at = ticket.CreatedAt if ticket.CreatedAt else current_time

            sla_log = SLALog(
                ticket_id=ticket.TicketID,
                escalation_level=escalation_level,
                level_name=level_name,
                sla_target_hours=sla_hours,
                status='on_time',
                created_at=created_at,
                logged_at=current_time,
                is_breached=False
            )

            db.session.add(sla_log)
            db.session.commit()

            logger.info(
                f"Created enhanced SLA log for ticket {ticket.TicketID}")
            return sla_log

        except Exception as e:
            logger.error(
                f"Error creating enhanced SLA log for ticket {getattr(ticket, 'TicketID', 'unknown')}: {e}")
            return None

    def _check_sla_breach_enhanced(self, sla_log):
        """Enhanced SLA breach check with robust validation"""
        try:
            from app import db

            # Validate SLA log data
            if not sla_log.created_at or not sla_log.sla_target_hours:
                logger.warning(
                    f"SLA log {sla_log.id} missing required data for breach check")
                return False

            current_time = datetime.now()
            sla_deadline = sla_log.created_at + \
                timedelta(hours=sla_log.sla_target_hours)

            # Check if SLA is breached
            is_breached = current_time > sla_deadline

            if is_breached and not sla_log.is_breached:
                # Update SLA log as breached
                sla_log.is_breached = True
                sla_log.breach_time = sla_deadline
                sla_log.status = 'breached'

                db.session.commit()

                logger.info(
                    f"SLA breached for ticket {sla_log.ticket_id} (Level: {sla_log.level_name})")
                return True

            return is_breached

        except Exception as e:
            logger.warning(
                f"Error checking SLA breach for log {sla_log.id}: {e}")
            return False

    def _process_escalations_enhanced(self):
        """Enhanced escalation processing with robust error handling"""
        try:
            from app import db
            from database import SLALog, TicketStatusLog, EscalationRule

            # Get breached SLA logs that need escalation
            try:
                breached_logs = SLALog.query.filter_by(
                    is_breached=True,
                    escalated_at=None
                ).all()
            except Exception as e:
                logger.warning(f"Could not query breached SLA logs: {e}")
                return

            for sla_log in breached_logs:
                try:
                    # Validate SLA log data
                    if not sla_log.ticket_id:
                        logger.warning(
                            f"SLA log {sla_log.id} has no ticket_id")
                        continue

                    # Get the ticket with error handling
                    from app import Ticket
                    ticket = Ticket.query.get(sla_log.ticket_id)
                    if not ticket:
                        logger.warning(
                            f"Ticket {sla_log.ticket_id} not found for SLA log {sla_log.id}")
                        continue

                    # Process escalation
                    self._escalate_ticket_enhanced(ticket, sla_log)

                except Exception as e:
                    logger.warning(
                        f"Error processing escalation for SLA log {sla_log.id}: {e}")
                    continue

            db.session.commit()

        except Exception as e:
            logger.error(f"Error in enhanced escalation processing: {e}")

    def _escalate_ticket_enhanced(self, ticket, sla_log):
        """Enhanced ticket escalation with robust error handling"""
        try:
            from app import db
            from database import TicketStatusLog

            # Determine next escalation level
            current_level = sla_log.escalation_level or 0
            next_level = min(current_level + 1, 2)  # Max level is 2 (YouCloud)

            # Update ticket escalation level
            old_level = ticket.escalation_level
            ticket.escalation_level = next_level

            # Update SLA log
            sla_log.escalated_at = datetime.now()

            # Create status log entry with validation
            try:
                status_log = TicketStatusLog(
                    ticket_id=ticket.TicketID,
                    old_status=ticket.Status,
                    new_status='escalated',
                    changed_by='SLA Monitor',
                    changed_by_type='system',
                    escalation_level=next_level,
                    sla_status='breached',
                    notes=f'Auto-escalated due to SLA breach (Level {current_level} -> {next_level})',
                    created_at=datetime.now(),
                    changed_at=datetime.now()
                )

                db.session.add(status_log)

            except Exception as e:
                logger.warning(
                    f"Could not create status log for ticket {ticket.TicketID}: {e}")

            # Update ticket status if not already escalated
            if ticket.Status != 'escalated':
                ticket.Status = 'escalated'

            db.session.commit()

            level_names = {0: 'Bot', 1: 'ICP', 2: 'YouCloud'}
            logger.info(
                f"Enhanced escalation: Ticket {ticket.TicketID} escalated from {level_names.get(current_level, 'Unknown')} to {level_names.get(next_level, 'Unknown')}")

        except Exception as e:
            logger.error(
                f"Error in enhanced ticket escalation for ticket {ticket.TicketID}: {e}")

    def _check_and_auto_escalate_tickets_enhanced(self):
        """Enhanced auto-escalation check with robust error handling"""
        try:
            from app import db, Ticket
            from database import SLALog

            # Get tickets that are past their SLA and should be auto-escalated
            current_time = datetime.now()

            try:
                tickets_to_escalate = db.session.query(Ticket, SLALog).join(
                    SLALog, Ticket.TicketID == SLALog.ticket_id
                ).filter(
                    Ticket.Status.in_(['open', 'in_progress']),
                    SLALog.is_breached == True,
                    SLALog.escalated_at.is_(None)
                ).all()
            except Exception as e:
                logger.warning(
                    f"Could not query tickets for auto-escalation: {e}")
                return

            for ticket, sla_log in tickets_to_escalate:
                try:
                    # Additional validation before escalation
                    if not ticket.TicketID or not sla_log.id:
                        continue

                    self._escalate_ticket_enhanced(ticket, sla_log)

                except Exception as e:
                    logger.warning(
                        f"Error in auto-escalation for ticket {getattr(ticket, 'TicketID', 'unknown')}: {e}")
                    continue

            db.session.commit()

        except Exception as e:
            logger.error(f"Error in enhanced auto-escalation check: {e}")


# Create the enhanced monitor instance
enhanced_sla_monitor = EnhancedSLAMonitor()
