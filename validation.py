import json
import utility

class Validation():
    def read_json_from_path(self,file_path):
        """
        Returns: JSON data 
        """
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    class FFValidation():
        def validate_mandatory_keys(self,json_data, mandatory_keys):
            """
            Validates if each dictionary in the list contains all the mandatory keys.

            Args:
            - json_data (list of dict): The JSON data to validate.
            - mandatory_keys (set): A set of mandatory keys that each dictionary must contain.

            Returns:
            - bool: True if all dictionaries contain all mandatory keys, False otherwise.
            - list: List of dictionaries that do not contain all mandatory keys.
            """
            invalid_entries = []
            for entry in json_data:
                if not all(key in entry for key in mandatory_keys):
                    invalid_entries.append(entry)

            return invalid_entries
        
        def calculate_rate_difference(self,json_data):
            """
            Calculates the rate difference between price_min and price_max for each item.

            Args:
            - json_data (list of dict): The JSON data to process.

            Returns:
            - dict: A dictionary with item id as the key and a nested dictionary containing
                    the price and rate difference.
            """
            result = {}
            for item in json_data:
                item_id = item["id"]
                price_min = item.get("price_min", 0)
                price_max = item.get("price_max", 0)
                rate_difference = price_max - price_min
                result[item_id] = [{"price": price_min}, {"rate_difference": rate_difference}]
            return result
        
        def check_variants_images_prices(self,json_data):
            """
            Checks if each variant has associated images and their respective prices.

            Args:
            - json_data (list of dict): The JSON data to process.

            Returns:
            - dict: A dictionary with item id as the key and a list of boolean values indicating
                    if each variant has images and prices.
            """
            result = {}
            for item in json_data:
                item_id = item["id"]
                variants = item.get("variants", [])
                images = item.get("images", [])
                images_exist = bool(images)
                variant_checks = []
                for variant in variants:
                    price_exists = "price" in variant and variant["price"] is not None
                    variant_checks.append({"images_exist": images_exist, "price_exists": price_exists})
                result[item_id] = variant_checks
            return result

    class LCValidatioin(FFValidation):
        def validate_mandatory_keys(self,json_data, mandatory_keys):
            return super().validate_mandatory_keys(json_data, mandatory_keys)
        
    class TJValidatioin(FFValidation):
        def validate_mandatory_keys(self,json_data, mandatory_keys):
            return super().validate_mandatory_keys(json_data, mandatory_keys)

    
validator = Validation()
# Data Prepration 
ff_data = validator.read_json_from_path(file_path="./output/foreignfortune.json")
tj_data = validator.read_json_from_path(file_path="./output/traderjoes.json")
lc_data = validator.read_json_from_path(file_path="./output/lechocolat.json")

#Get all Class
ff_validator = validator.FFValidation()
lc_validator = validator.LCValidatioin()
tj_validator = validator.TJValidatioin()

# data without mandatory keys
ff_invalid_data = ff_validator.validate_mandatory_keys(json_data=ff_data,mandatory_keys=["id","title","price","vendor"])
lc_invalid_data = lc_validator.validate_mandatory_keys(json_data=lc_data,mandatory_keys=["id","title","price","description","categoty"])
tj_invalid_data = tj_validator.validate_mandatory_keys(json_data=tj_data,mandatory_keys=["id","title","price","category","unit"])

# Calculate Rate Difference
ff_rate_diff = ff_validator.calculate_rate_difference(ff_data)

# check variants 
ff_variant = ff_validator.check_variants_images_prices(ff_data)


consolidated_data = {
    "ff_invalid_data": {
        "invalid_entries": ff_invalid_data
    },
    "lc_invalid_data": {
        "invalid_entries": lc_invalid_data
    },
    "tj_invalid_data": {
        "invalid_entries": tj_invalid_data
    },
    "ff_rate_diff": ff_rate_diff,
    "ff_variants": ff_variant
}

utility.output(consolidated_data,"./validation.json")
print("Completed Validation.....")