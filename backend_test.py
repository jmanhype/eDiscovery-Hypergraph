#!/usr/bin/env python3
import requests
import json
import unittest
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("eDiscovery-Test")

# Base URL for the eDiscovery API
BASE_URL = "http://localhost:4000/api"

class EDiscoveryAPITest(unittest.TestCase):
    """Test suite for eDiscovery Agent MVP backend API"""

    def test_01_health_check(self):
        """Test the health check endpoint"""
        logger.info("Testing health check endpoint...")
        
        response = requests.get(f"{BASE_URL}/ediscovery/health")
        
        self.assertEqual(response.status_code, 200, "Health check should return 200 OK")
        
        data = response.json()
        logger.info(f"Health check response: {json.dumps(data, indent=2)}")
        
        self.assertEqual(data["status"], "healthy", "Health status should be 'healthy'")
        self.assertIn("service", data, "Health check should include service info")
        self.assertEqual(data["service"], "eDiscovery Agent", "Service name should be 'eDiscovery Agent'")

    def test_02_sample_endpoint(self):
        """Test the sample endpoint"""
        logger.info("Testing sample endpoint...")
        
        response = requests.get(f"{BASE_URL}/ediscovery/sample")
        
        self.assertEqual(response.status_code, 200, "Sample endpoint should return 200 OK")
        
        data = response.json()
        logger.info(f"Sample endpoint response: {json.dumps(data, indent=2)}")
        
        self.assertIn("sample_request", data, "Sample should include a sample request")
        self.assertIn("emails", data["sample_request"], "Sample should include emails array")

    def test_03_process_emails(self):
        """Test the email processing endpoint with valid data"""
        logger.info("Testing email processing endpoint with valid data...")
        
        # Sample email data from the requirements
        payload = {
            "emails": [
                {
                    "from_addr": "alice@company.com",
                    "to": ["bob@company.com"],
                    "subject": "Confidential Legal Matter - Project X",
                    "date": "2024-01-15T10:30:00Z", 
                    "body": "Hi Bob,\n\nI wanted to discuss the confidential matters regarding Project X with our legal counsel. The attorney-client privileged documents need immediate review for the upcoming litigation.\n\nThis contains significant evidence for the case.\n\nBest regards,\nAlice"
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BASE_URL}/ediscovery/process", 
            data=json.dumps(payload), 
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200, "Process endpoint should return 200 OK")
        
        data = response.json()
        logger.info(f"Process endpoint response: {json.dumps(data, indent=2)}")
        
        # Validate response structure
        self.assertEqual(data["status"], "success", "Process status should be 'success'")
        self.assertIn("batch_id", data, "Response should include batch_id")
        self.assertIn("processed_count", data, "Response should include processed_count")
        self.assertIn("results", data, "Response should include results")
        self.assertEqual(data["processed_count"], 1, "Should have processed 1 email")
        
        # Validate email analysis result
        result = data["results"][0]
        self.assertIn("email_id", result, "Result should include email_id")
        self.assertIn("batch_id", result, "Result should include batch_id")
        self.assertIn("metadata", result, "Result should include metadata")
        self.assertIn("summary", result, "Result should include summary")
        self.assertIn("tags", result, "Result should include tags")
        self.assertIn("entities", result, "Result should include entities")
        
        # Validate tags (privileged and significant_evidence should be true)
        tags = result["tags"]
        self.assertIn("privileged", tags, "Tags should include privileged flag")
        self.assertIn("significant_evidence", tags, "Tags should include significant_evidence flag")
        
        # Check if the tags are correctly identified (should be true based on the email content)
        logger.info(f"Tags: privileged={tags.get('privileged')}, significant_evidence={tags.get('significant_evidence')}")
        self.assertTrue(tags.get("privileged"), "Email should be identified as privileged")
        self.assertTrue(tags.get("significant_evidence"), "Email should be identified as containing significant evidence")
        
        # Check entities extraction
        entities = result["entities"]
        logger.info(f"Extracted entities: {entities}")
        
        # Check if key entities are extracted (Alice, Bob, Project X)
        entity_names = [entity["name"].lower() for entity in entities]
        self.assertTrue(any("alice" in name for name in entity_names), "Should extract 'Alice' as an entity")
        self.assertTrue(any("bob" in name for name in entity_names), "Should extract 'Bob' as an entity")
        self.assertTrue(any("project x" in name for name in entity_names), "Should extract 'Project X' as an entity")

    def test_04_process_emails_malformed(self):
        """Test the email processing endpoint with malformed data"""
        logger.info("Testing email processing endpoint with malformed data...")
        
        # Malformed payload (missing required fields)
        payload = {
            "emails": [
                {
                    # Missing from, to, subject, date
                    "body": "This is a test email with missing fields."
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BASE_URL}/ediscovery/process", 
            data=json.dumps(payload), 
            headers=headers
        )
        
        # Should still work with default values for missing fields
        self.assertEqual(response.status_code, 200, "Process endpoint should handle missing fields")
        
        data = response.json()
        logger.info(f"Process endpoint response (malformed data): {json.dumps(data, indent=2)}")
        
        # Validate response structure
        self.assertEqual(data["status"], "success", "Process status should be 'success' even with missing fields")
        
        # Validate email analysis result
        result = data["results"][0]
        self.assertIn("metadata", result, "Result should include metadata")
        
        # Check that metadata exists but don't assert specific field names
        # as they may vary in the implementation
        metadata = result["metadata"]
        self.assertTrue(any(key in ["from", "from_addr"] for key in metadata.keys()), 
                       "Metadata should include sender information (from or from_addr)")
        self.assertIn("subject", metadata, "Metadata should include subject")

    def test_05_process_emails_invalid_json(self):
        """Test the email processing endpoint with invalid JSON"""
        logger.info("Testing email processing endpoint with invalid JSON...")
        
        # Invalid JSON payload
        invalid_payload = "{ this is not valid JSON }"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BASE_URL}/ediscovery/process", 
            data=invalid_payload, 
            headers=headers
        )
        
        # Should return an error
        self.assertNotEqual(response.status_code, 200, "Process endpoint should reject invalid JSON")
        logger.info(f"Process endpoint response (invalid JSON): {response.status_code} - {response.text}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
