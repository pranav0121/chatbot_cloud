"""
Odoo Integration Service for Chatbot Cloud System
Handles all Odoo API interactions using XML-RPC
"""

import xmlrpc.client
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class OdooService:
    """Service class for Odoo API integration"""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Initialize Odoo service
        
        Args:
            url: Odoo server URL (e.g., https://youcloudpay.odoo.com)
            db: Database name (e.g., youcloudpay)
            username: Odoo login username
            password: Odoo login password
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        
        # Initialize XML-RPC clients
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Authenticate
        try:
            self.authenticate()
            logger.info(f"Successfully connected to Odoo at {url}")
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            raise
    
    def authenticate(self) -> int:
        """Authenticate with Odoo and get user ID"""
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if not self.uid:
                raise Exception("Authentication failed - check credentials")
            logger.info(f"Authenticated as user ID: {self.uid}")
            return self.uid
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Odoo connection and return status"""
        try:
            # Get version info
            version = self.common.version()
            
            # Get user info
            user_info = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.users', 'read',
                [self.uid], {'fields': ['name', 'email', 'login']}
            )
            
            return {
                'status': 'success',
                'connected': True,
                'version': version,
                'user': user_info[0] if user_info else None,
                'url': self.url,
                'database': self.db
            }
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                'status': 'error',
                'connected': False,
                'error': str(e),
                'url': self.url,
                'database': self.db
            }
    
    def create_customer(self, name: str, email: str = None, phone: str = None, **kwargs) -> int:
        """
        Create a new customer in Odoo
        
        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone            **kwargs: Additional customer fields
            
        Returns:
            Customer ID
        """
        try:
            customer_data = {
                'name': name,
                'is_company': False,
                'customer_rank': 1,  # Mark as customer
            }
            
            if email:
                customer_data['email'] = email
            if phone:
                customer_data['phone'] = phone
                
            # Handle company field specially
            if 'company' in kwargs:
                company_name = kwargs.pop('company')
                # Set company as a comment or in the name
                if company_name:
                    customer_data['comment'] = f"Company: {company_name}"
                    # Or combine with name: customer_data['name'] = f"{name} ({company_name})"
                
            # Add any additional fields (excluding invalid ones)
            valid_fields = {'street', 'city', 'zip', 'country_id', 'state_id', 'website', 'mobile', 'function', 'title', 'comment'}
            for key, value in kwargs.items():
                if key in valid_fields:
                    customer_data[key] = value
            
            customer_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'create',
                [customer_data]
            )
            
            logger.info(f"Created customer {name} with ID: {customer_id}")
            return customer_id
            
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            raise
    
    def get_customers(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get list of customers from Odoo"""
        try:
            customers = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search_read',
                [[['customer_rank', '>', 0]]],
                {
                    'fields': ['id', 'name', 'email', 'phone', 'create_date'],
                    'limit': limit,
                    'offset': offset,
                    'order': 'create_date desc'
                }
            )
            return customers
        except Exception as e:
            logger.error(f"Failed to get customers: {e}")
            raise
    
    def get_or_create_tag(self, tag_name: str) -> int:
        """
        Get existing tag ID or create a new tag
        
        Args:
            tag_name: Name of the tag
            
        Returns:
            Tag ID
        """
        try:
            # Try to find existing tag
            tag_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'helpdesk.tag', 'search',
                [[['name', '=', tag_name]]]
            )
            
            if tag_ids:
                logger.info(f"Found existing tag '{tag_name}' with ID: {tag_ids[0]}")
                return tag_ids[0]
            
            # Create new tag if not found
            tag_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'helpdesk.tag', 'create',
                [{'name': tag_name}]
            )
            
            logger.info(f"Created new tag '{tag_name}' with ID: {tag_id}")
            return tag_id
            
        except Exception as e:
            logger.error(f"Failed to get/create tag '{tag_name}': {e}")
            # Return None if tag creation fails - we'll handle this gracefully
            return None

    def create_ticket(self, name: str, description: str, partner_id: int = None, 
                     priority: str = '1', **kwargs) -> int:
        """
        Create a helpdesk ticket in Odoo
        
        Args:
            name: Ticket subject
            description: Ticket description
            partner_id: Customer ID (optional)
            priority: Ticket priority (0=Low, 1=Normal, 2=High, 3=Urgent)
            **kwargs: Additional ticket fields
            
        Returns:
            Ticket ID
        """
        try:
            ticket_data = {
                'name': name,
                'description': description,
                'priority': priority,
            }
            
            if partner_id:
                ticket_data['partner_id'] = partner_id
                
            # Handle tag_ids specially - convert tag names to tag IDs
            if 'tag_ids' in kwargs:
                tag_names = kwargs.pop('tag_ids')  # Remove from kwargs
                if tag_names:
                    tag_ids = []
                    for tag_name in tag_names:
                        tag_id = self.get_or_create_tag(tag_name)
                        if tag_id:
                            tag_ids.append(tag_id)
                    
                    if tag_ids:
                        # Odoo expects tag_ids in format [(6, 0, [tag_id1, tag_id2, ...])]
                        ticket_data['tag_ids'] = [(6, 0, tag_ids)]
                
            # Add any remaining additional fields
            ticket_data.update(kwargs)
            
            ticket_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'helpdesk.ticket', 'create',
                [ticket_data]
            )
            
            logger.info(f"Created ticket '{name}' with ID: {ticket_id}")
            return ticket_id
            
        except Exception as e:
            logger.error(f"Failed to create ticket: {e}")
            raise
    
    def get_tickets(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get list of helpdesk tickets from Odoo"""
        try:
            tickets = self.models.execute_kw(
                self.db, self.uid, self.password,
                'helpdesk.ticket', 'search_read',
                [[]],
                {
                    'fields': ['id', 'name', 'description', 'priority', 'stage_id', 
                              'partner_id', 'create_date', 'write_date'],
                    'limit': limit,
                    'offset': offset,
                    'order': 'create_date desc'
                }
            )
            return tickets
        except Exception as e:
            logger.error(f"Failed to get tickets: {e}")
            raise
    
    def update_ticket(self, ticket_id: int, **kwargs) -> bool:
        """Update a helpdesk ticket"""
        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                'helpdesk.ticket', 'write',
                [[ticket_id], kwargs]
            )
            logger.info(f"Updated ticket {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to update ticket {ticket_id}: {e}")
            raise
    
    def search_customers(self, query: str, limit: int = 10) -> List[Dict]:
        """Search customers by name or email"""
        try:
            domain = [
                '|', 
                ['name', 'ilike', query],
                ['email', 'ilike', query],
                ['customer_rank', '>', 0]
            ]
            
            customers = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search_read',
                [domain],
                {
                    'fields': ['id', 'name', 'email', 'phone'],
                    'limit': limit
                }
            )
            return customers
        except Exception as e:
            logger.error(f"Failed to search customers: {e}")
            raise
    
    def get_customer_tickets(self, partner_id: int, limit: int = 10) -> List[Dict]:
        """Get tickets for a specific customer"""
        try:
            tickets = self.models.execute_kw(
                self.db, self.uid, self.password,
                'helpdesk.ticket', 'search_read',
                [[['partner_id', '=', partner_id]]],
                {
                    'fields': ['id', 'name', 'description', 'priority', 'stage_id', 'create_date'],
                    'limit': limit,
                    'order': 'create_date desc'
                }
            )
            return tickets
        except Exception as e:
            logger.error(f"Failed to get customer tickets: {e}")
            raise
