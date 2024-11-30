import random
import json
import boto3
import logging

# DynamoDB table configuration
DYNAMODB_TABLE = "DrinksTable"
dynamodb = boto3.resource("dynamodb")

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def fetch_drinks_from_dynamodb():
    """Fetch the list of drinks from DynamoDB."""
    try:
        logger.info("Fetching drinks from DynamoDB.")
        table = dynamodb.Table(DYNAMODB_TABLE)
        response = table.get_item(Key={"category": "drinks"})
        if "Item" in response:
            drinks = response["Item"].get("drinks", [])
            logger.info(f"Successfully fetched drinks: {drinks}")
            return drinks
        else:
            logger.warning("No drinks found in the database.")
            return []
    except Exception as e:
        logger.error(f"Error fetching drinks from DynamoDB: {str(e)}", exc_info=True)
        return []

def random_drink(drinks):
    """Pick a random drink from the list."""
    logger.info("Choosing a random drink.")
    return random.choice(drinks)

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle the main drink endpoint
        query_params = event.get("queryStringParameters", {})
        name_customer = query_params.get("name", "Guest")
        chosen_drink = query_params.get("choice", None)
        logger.info(f"Query parameters: name={name_customer}, choice={chosen_drink}")
        
        # Fetch drinks dynamically from DynamoDB
        drinks = fetch_drinks_from_dynamodb()
        if not drinks:
            logger.error("Drinks list is empty. Unable to proceed.")
            return {
                'statusCode': 500,
                'body': json.dumps({"error": "No drinks available in the database."})
            }
        if chosen_drink:    
            chosen_drink = chosen_drink.strip().capitalize()
            if chosen_drink in [drink.capitalize() for drink in drinks]:
                message = f"{name_customer}, You chose {chosen_drink}."
                logger.info(f"Customer chose a valid drink: {chosen_drink}")
            else:
                message = (
                    f"{name_customer}, '{chosen_drink}' is not available. "
                    f"Please choose from: {', '.join(drinks)}."
                )
                logger.warning(f"Invalid drink choice: {chosen_drink}")
        else:
            # No choice made, system chooses a random drink
            drink = random_drink(drinks)
            message = f"{name_customer}, You didn't choose a drink, so we picked {drink} for you."
            logger.info(f"No choice provided. Randomly picked drink: {drink}")
        
        logger.info("Successfully generated response.")
        return {
            'statusCode': 200,
            'body': json.dumps({"message": message})
        }
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({"error": f"An error occurred: {str(e)}"})
        }
