#!/usr/bin/env python3

import asyncio
import time
import sys
import os
import httpx
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test the complete dispute resolution flow

API_BASE = "http://localhost:8000"
API_KEY = "changeme"

async def test_full_flow():
    """Test the complete dispute resolution pipeline"""
    
    # Test cases with different dispute types
    test_cases = [
        {
            "narrative": "I did not authorize this transaction. My card was stolen and this charge appeared on my account.",
            "amount": 5000,  # $50.00
            "currency": "USD",
            "customer_id": "cust_0001",
            "merchant_id": "amzn_shop",
            "external_ref": "REF_001",
            "expected_classification": "FRAUD_UNAUTHORIZED"
        },
        {
            "narrative": "I ordered a laptop but received a broken tablet instead. The merchant charged me the wrong amount.",
            "amount": 120000,  # $1200.00
            "currency": "USD", 
            "customer_id": "cust_0002",
            "merchant_id": "electronics_hub",
            "external_ref": "REF_002",
            "expected_classification": "MERCHANT_ERROR"
        },
        {
            "narrative": "I never received the item I ordered 3 weeks ago. The package tracking shows it was never shipped.",
            "amount": 8000,  # $80.00
            "currency": "USD",
            "customer_id": "cust_0003", 
            "merchant_id": "fashion_store",
            "external_ref": "REF_003",
            "expected_classification": "SERVICE_NOT_RECEIVED"
        },
        {
            "narrative": "My child used my card to make purchases without my permission. I need these charges reversed.",
            "amount": 2500,  # $25.00
            "currency": "USD",
            "customer_id": "cust_0004",
            "merchant_id": "app_store",
            "external_ref": "REF_004", 
            "expected_classification": "FRIENDLY_FRAUD_RISK"
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        
        print("🚀 Testing LLM Dispute Resolution System")
        print("=" * 50)
        
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = await client.get(f"{API_BASE}/v1/health", headers=headers)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
        
        dispute_ids = []
        
        # Process each test case
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i+1}. Processing dispute: {test_case['expected_classification']}")
            print(f"   Narrative: {test_case['narrative'][:60]}...")
            
            # Create dispute payload
            payload = {
                "narrative": test_case["narrative"],
                "amount": test_case["amount"],
                "currency": test_case["currency"],
                "customer_id": test_case["customer_id"],
                "merchant_id": test_case["merchant_id"],
                "external_ref": test_case["external_ref"]
            }
            
            # Submit dispute
            start_time = time.time()
            response = await client.post(f"{API_BASE}/v1/disputes", json=payload, headers=headers)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                dispute_id = result["id"]
                dispute_ids.append(dispute_id)
                
                print(f"   ✅ Dispute created: {dispute_id}")
                print(f"   📊 Classification: {result['classification']['label']} (confidence: {result['classification']['confidence']:.2f})")
                print(f"   🎯 Recommendation: {result['recommendation']['action']} (confidence: {result['recommendation']['confidence']:.2f})")
                print(f"   ⏱️  Latency: {result['latency_ms']}ms (end-to-end: {(end_time - start_time)*1000:.0f}ms)")
                
                # Verify classification
                if result['classification']['label'] == test_case['expected_classification']:
                    print("   ✅ Classification matches expected")
                else:
                    print(f"   ⚠️  Classification mismatch. Expected: {test_case['expected_classification']}, Got: {result['classification']['label']}")
                    
            else:
                print(f"   ❌ Failed to create dispute: {response.status_code}")
                print(f"   Error: {response.text}")
        
        # Test retrieval and audit logs
        if dispute_ids:
            print(f"\n{len(test_cases)+2}. Testing dispute retrieval...")
            dispute_id = dispute_ids[0]
            
            # Get dispute by ID
            response = await client.get(f"{API_BASE}/v1/disputes/{dispute_id}", headers=headers)
            if response.status_code == 200:
                print("   ✅ Dispute retrieval successful")
            else:
                print(f"   ❌ Dispute retrieval failed: {response.status_code}")
            
            # Get audit log
            response = await client.get(f"{API_BASE}/v1/disputes/{dispute_id}/audit", headers=headers)
            if response.status_code == 200:
                audit_log = response.json()
                print(f"   ✅ Audit log retrieved: {len(audit_log['events'])} events")
                for event in audit_log['events']:
                    print(f"      - {event['step']}: {event['latency_ms']}ms ({'✅' if event['success'] else '❌'})")
            else:
                print(f"   ❌ Audit log retrieval failed: {response.status_code}")
        
        # Test metrics
        print(f"\n{len(test_cases)+3}. Testing metrics endpoint...")
        response = await client.get(f"{API_BASE}/v1/metrics", headers=headers)
        if response.status_code == 200:
            metrics = response.json()
            print("   ✅ Metrics retrieved:")
            print(f"      - Total cases: {metrics['total_cases']}")
            print(f"      - Avg classification latency (p95): {metrics['classification_latency_ms_p95']:.1f}ms")
            print(f"      - Avg recommendation latency (p95): {metrics['recommendation_latency_ms_p95']:.1f}ms")
            print(f"      - Avg cost per case: ${metrics['avg_cost_per_case_usd']:.4f}")
            print(f"      - Cases by label: {metrics['cases_by_label']}")
        else:
            print(f"   ❌ Metrics retrieval failed: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎉 Test flow completed!")

async def test_legacy_api():
    """Test the legacy v0 API for backwards compatibility"""
    print("\n🔄 Testing legacy API (v0)...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        
        # Test simple classification
        payload = {"narrative": "This is a fraudulent charge on my account"}
        response = await client.post(f"{API_BASE}/disputes/classify", json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Legacy classification: {result['classification']}")
        else:
            print(f"   ❌ Legacy API failed: {response.status_code}")

if __name__ == "__main__":
    print("Starting comprehensive test suite...")
    print("Make sure the server is running with: uvicorn app.main:app --reload")
    
    try:
        asyncio.run(test_full_flow())
        asyncio.run(test_legacy_api())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
    }
    resp = client.post("/v1/disputes", json=payload)
    assert resp.status_code == 422

    # Negative amount
    payload = {
        "external_ref": "CASE-4",
        "customer_id": "c-4",
        "merchant_id": "m-4",
        "amount": -50,
        "currency": "USD",
        "narrative": "Test narrative"
    }
    resp = client.post("/v1/disputes", json=payload)
    assert resp.status_code == 422

    # Too long narrative
    payload = {
        "external_ref": "CASE-5",
        "customer_id": "c-5",
        "merchant_id": "m-5",
        "amount": 100,
        "currency": "USD",
        "narrative": "A" * 6000
    }
    resp = client.post("/v1/disputes", json=payload)
    assert resp.status_code == 201  # Should be truncated, not rejected

    # Invalid customer_id (empty string)
    payload = {
        "external_ref": "CASE-6",
        "customer_id": "",
        "merchant_id": "m-6",
        "amount": 100,
        "currency": "USD",
        "narrative": "Test narrative"
    }
    resp = client.post("/v1/disputes", json=payload)
    assert resp.status_code == 422
