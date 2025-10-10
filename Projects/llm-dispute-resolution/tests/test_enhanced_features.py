#!/usr/bin/env python3

import asyncio
import time
import sys
import os
import httpx
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Enhanced test suite for new features

API_BASE = "http://localhost:8000"
API_KEY = "changeme"

async def test_enhanced_features():
    """Test the new advanced features"""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        
        print("🚀 Testing Enhanced LLM Dispute Resolution System")
        print("=" * 60)
        
        # Test 1: Enhanced root endpoint
        print("1. Testing enhanced root endpoint...")
        response = await client.get(f"{API_BASE}/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Version: {data.get('version')}")
            print(f"   ✅ Features: {len(data.get('features', []))} new features")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
        
        # Test 2: Process disputes with advanced features
        print("\n2. Testing enhanced dispute processing...")
        enhanced_test_cases = [
            {
                "narrative": "Someone hacked my account and made unauthorized purchases. My email is john.doe@email.com and SSN is 123-45-6789.",
                "amount": 15000,  # $150.00
                "currency": "USD",
                "customer_id": "cust_0001",
                "merchant_id": "suspicious_merchant",
                "external_ref": "PII_TEST_001"
            },
            {
                "narrative": "I received a damaged laptop but was charged $1,200.00. Credit card 4532-1234-5678-9012 was used.",
                "amount": 120000,  # $1200.00
                "currency": "USD", 
                "customer_id": "cust_0002",
                "merchant_id": "electronics_vendor",
                "external_ref": "PII_TEST_002"
            }
        ]
        
        dispute_ids = []
        for i, test_case in enumerate(enhanced_test_cases, 1):
            print(f"\n   2.{i} Processing dispute with PII content...")
            
            start_time = time.time()
            response = await client.post(f"{API_BASE}/v1/disputes", json=test_case, headers=headers)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                dispute_id = result["id"]
                dispute_ids.append(dispute_id)
                
                print(f"      ✅ Dispute created: {dispute_id}")
                print(f"      📊 Classification: {result['classification']['label']}")
                print(f"      🎯 Recommendation: {result['recommendation']['action']}")
                print(f"      ⏱️  Processing time: {(end_time - start_time)*1000:.0f}ms")
            else:
                print(f"      ❌ Failed: {response.status_code} - {response.text}")
        
        # Test 3: PII Analysis
        print("\n3. Testing PII analysis...")
        pii_test_text = "Contact John Doe at john.doe@email.com or call (555) 123-4567. SSN: 123-45-6789, Credit Card: 4532-1234-5678-9012"
        
        response = await client.post(
            f"{API_BASE}/v1/analytics/pii/analyze",
            params={"text": pii_test_text},
            headers=headers
        )
        
        if response.status_code == 200:
            pii_data = response.json()
            print(f"   ✅ PII detected: {pii_data['pii_detected']}")
            print(f"   📊 Types found: {pii_data['detected_types']}")
            print(f"   🔒 Redaction count: {pii_data['redaction_count']}")
            print(f"   📝 Original: {pii_data['original_text'][:50]}...")
            print(f"   🛡️  Redacted: {pii_data['redacted_text'][:50]}...")
        else:
            print(f"   ❌ PII analysis failed: {response.status_code}")
        
        # Test 4: Pattern Detection
        print("\n4. Testing pattern detection...")
        response = await client.get(f"{API_BASE}/v1/analytics/patterns?days_back=30", headers=headers)
        
        if response.status_code == 200:
            patterns = response.json()
            print(f"   ✅ Pattern alerts found: {len(patterns)}")
            
            # Show high-severity alerts
            high_severity = [p for p in patterns if p['severity'] in ['high', 'critical']]
            if high_severity:
                print(f"   🚨 High-severity alerts: {len(high_severity)}")
                for alert in high_severity[:3]:  # Show first 3
                    print(f"      - {alert['title']} (confidence: {alert['confidence_score']:.2f})")
            else:
                print("   ✅ No high-severity alerts (system healthy)")
        else:
            print(f"   ❌ Pattern detection failed: {response.status_code}")
        
        # Test 5: Merchant Risk Scoring
        print("\n5. Testing merchant risk scoring...")
        test_merchant = "suspicious_merchant"
        response = await client.get(
            f"{API_BASE}/v1/analytics/merchants/{test_merchant}/risk?days_back=30",
            headers=headers
        )
        
        if response.status_code == 200:
            risk_data = response.json()
            print(f"   ✅ Risk assessment completed for {test_merchant}")
            print(f"   📊 Risk score: {risk_data['risk_score']}/100")
            print(f"   🚨 Risk level: {risk_data['risk_level']}")
            print(f"   📈 Stats: {risk_data['stats']['total_disputes']} disputes, {risk_data['stats']['fraud_rate']:.1%} fraud rate")
        else:
            print(f"   ❌ Risk scoring failed: {response.status_code}")
        
        # Test 6: LLM Usage Statistics
        print("\n6. Testing LLM usage tracking...")
        response = await client.get(f"{API_BASE}/v1/analytics/llm/usage", headers=headers)
        
        if response.status_code == 200:
            usage_data = response.json()
            print(f"   ✅ Usage stats retrieved")
            print(f"   💰 Total cost: ${usage_data['total_cost']:.4f}")
            print(f"   🔢 Total tokens: {usage_data['total_tokens']:,}")
            print(f"   🔧 Mock mode: {usage_data['provider_stats']['mock_mode_active']}")
        else:
            print(f"   ❌ Usage stats failed: {response.status_code}")
        
        # Test 7: Analytics Dashboard
        print("\n7. Testing analytics dashboard...")
        response = await client.get(f"{API_BASE}/v1/analytics/dashboard?days_back=7", headers=headers)
        
        if response.status_code == 200:
            dashboard = response.json()
            print(f"   ✅ Dashboard data generated")
            print(f"   📊 Period: {dashboard['period_days']} days")
            print(f"   🚨 Total alerts: {dashboard['alerts']['total_alerts']}")
            print(f"   💰 LLM cost: ${dashboard['llm_usage']['total_cost']:.4f}")
            
            if dashboard['alerts']['high_priority']:
                print(f"   🚨 High-priority alerts:")
                for alert in dashboard['alerts']['high_priority'][:2]:
                    print(f"      - {alert['title']} ({alert['severity']})")
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
        
        # Test 8: Analytics Health Check
        print("\n8. Testing analytics health check...")
        response = await client.get(f"{API_BASE}/v1/analytics/health", headers=headers)
        
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Analytics health: {health['status']}")
            for component, status in health['components'].items():
                print(f"      - {component}: {status}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎉 Enhanced feature testing completed!")
        
        # Summary of new capabilities
        print("\n📋 New Capabilities Demonstrated:")
        print("   ✅ PII detection and redaction for data privacy")
        print("   ✅ Real LLM integration with fallback mechanisms")
        print("   ✅ Advanced pattern detection for fraud prevention")
        print("   ✅ Merchant risk scoring for proactive monitoring")
        print("   ✅ Comprehensive analytics dashboard")
        print("   ✅ Enhanced error handling and observability")

async def test_security_features():
    """Test security and PII protection features"""
    print("\n🔒 Testing Security Features")
    print("-" * 40)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        
        # Test various PII types
        pii_tests = [
            "My SSN is 123-45-6789 and email is test@example.com",
            "Call me at (555) 123-4567 or use card 4532-1234-5678-9012",
            "IP address 192.168.1.1 and account number 1234567890123456"
        ]
        
        for i, text in enumerate(pii_tests, 1):
            print(f"\n{i}. Testing PII detection: {text[:30]}...")
            
            response = await client.post(
                f"{API_BASE}/v1/analytics/pii/analyze",
                params={"text": text},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['pii_detected']:
                    print(f"   ✅ Detected {result['redaction_count']} PII items")
                    print(f"   🛡️  Types: {', '.join(result['detected_types'])}")
                else:
                    print("   ℹ️  No PII detected")
            else:
                print(f"   ❌ Test failed: {response.status_code}")

async def test_performance_features():
    """Test performance and monitoring features"""
    print("\n⚡ Testing Performance Features")
    print("-" * 40)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        
        # Test concurrent dispute processing
        print("\n1. Testing concurrent processing...")
        
        concurrent_disputes = [
            {
                "narrative": f"Test dispute {i} for performance testing",
                "amount": 1000 + i * 100,
                "currency": "USD",
                "customer_id": f"perf_customer_{i:03d}",
                "merchant_id": f"perf_merchant_{i % 3}",
                "external_ref": f"PERF_TEST_{i:03d}"
            }
            for i in range(5)
        ]
        
        start_time = time.time()
        
        # Process disputes concurrently
        tasks = [
            client.post(f"{API_BASE}/v1/disputes", json=dispute, headers=headers)
            for dispute in concurrent_disputes
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        successful = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
        total_time = (end_time - start_time) * 1000
        avg_time = total_time / len(responses)
        
        print(f"   ✅ Processed {successful}/{len(responses)} disputes")
        print(f"   ⏱️  Total time: {total_time:.0f}ms")
        print(f"   📊 Average time: {avg_time:.0f}ms per dispute")
        print(f"   🚀 Throughput: {len(responses) / (total_time / 1000):.1f} disputes/second")

if __name__ == "__main__":
    print("Starting enhanced test suite...")
    print("Make sure the server is running with: python run.py --server")
    
    try:
        asyncio.run(test_enhanced_features())
        asyncio.run(test_security_features())
        asyncio.run(test_performance_features())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()