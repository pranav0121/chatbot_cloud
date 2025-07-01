#!/usr/bin/env python3
"""
Check available routes in the Flask app
"""

def check_routes():
    """Check all available routes in the Flask app"""
    
    try:
        from app import app
        
        with app.app_context():
            print("=== AVAILABLE ROUTES ===\n")
            
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'rule': rule.rule
                })
            
            # Sort routes by rule
            routes.sort(key=lambda x: x['rule'])
            
            print("Super Admin Routes:")
            for route in routes:
                if 'super-admin' in route['rule'] or 'super_admin' in route['endpoint']:
                    methods = [m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']]
                    print(f"  {route['rule']} | {methods} | {route['endpoint']}")
            
            print("\nEscalation Related Routes:")
            for route in routes:
                if 'escalat' in route['rule'].lower() or 'escalat' in route['endpoint'].lower():
                    methods = [m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']]
                    print(f"  {route['rule']} | {methods} | {route['endpoint']}")
            
            print("\nAPI Routes:")
            for route in routes:
                if '/api/' in route['rule']:
                    methods = [m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']]
                    print(f"  {route['rule']} | {methods} | {route['endpoint']}")
                    
    except Exception as e:
        print(f"Error checking routes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_routes()
