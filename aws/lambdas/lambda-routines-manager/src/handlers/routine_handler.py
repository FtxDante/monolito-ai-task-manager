import json
import logging
from src.services.routine_service import RoutineService
from src.utils.decimal_encoder import DecimalEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function handler for routines management
    """
    try:
        logger.info('Event: %s', json.dumps(event))
        
        # Initialize service
        service = RoutineService()
        
        # Get HTTP method from the event
        http_method = event.get('httpMethod', 'GET')
        
        # Get path parameters
        path_parameters = event.get('pathParameters', {})
        routine_id = path_parameters.get('id') if path_parameters else None
        
        # Determine the route
        route = f"{http_method} /routines"
        if routine_id:
            route = f"{http_method} /routines/{routine_id}"
        
        if http_method == 'GET':
            # Check if we're getting a specific routine or listing all
            if routine_id:
                routine = service.get_routine(routine_id)
                if not routine:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({
                            'message': f"Routine not found at {route}",
                            'data': None
                        })
                    }
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': f"Successfully retrieved routine at {route}",
                        'data': routine.to_dict()
                    }, cls=DecimalEncoder)
                }
            else:
                routines = service.list_routines()
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': f"Successfully retrieved routines at {route}",
                        'data': [r.to_dict() for r in routines]
                    }, cls=DecimalEncoder)
                }
        
        elif http_method == 'POST':
            # Create a new routine
            try:
                body = json.loads(event.get('body', '{}'))
                routine = service.create_routine(body)
                return {
                    'statusCode': 201,
                    'body': json.dumps({
                        'message': f"Successfully created routine at {route}",
                        'data': routine.to_dict()
                    }, cls=DecimalEncoder)
                }
            except ValueError as e:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f"Error creating routine at {route}: {str(e)}",
                        'data': None
                    })
                }
                
        elif http_method == 'PUT':
            # Update an existing routine
            if not routine_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f"Missing routine ID at {route}",
                        'data': None
                    })
                }
                
            try:
                body = json.loads(event.get('body', '{}'))
                updated_routine = service.update_routine(routine_id, body)
                
                if not updated_routine:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({
                            'message': f"Routine not found at {route}",
                            'data': None
                        })
                    }
                    
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': f"Successfully updated routine at {route}",
                        'data': updated_routine.to_dict()
                    }, cls=DecimalEncoder)
                }
            except ValueError as e:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f"Error updating routine at {route}: {str(e)}",
                        'data': None
                    })
                }
                
        elif http_method == 'DELETE':
            # Delete a routine
            if not routine_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f"Missing routine ID at {route}",
                        'data': None
                    })
                }
                
            deleted = service.delete_routine(routine_id)
            if not deleted:
                return {
                    'statusCode': 404,
                    'body': json.dumps({
                        'message': f"Routine not found at {route}",
                        'data': None
                    })
                }
                
            return {
                'statusCode': 204,
                'body': json.dumps({
                    'message': f"Successfully deleted routine at {route}",
                    'data': None
                })
            }
        
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"Unsupported HTTP method at {route}",
                'data': None
            })
        }
        
    except Exception as e:
        logger.error('Error: %s', str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Internal server error: {str(e)}",
                'data': None
            })
        } 