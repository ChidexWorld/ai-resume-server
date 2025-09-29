#!/usr/bin/env python3
"""
Test script for the employer dashboard integration.
This script tests the dashboard functionality without running the full server.
"""

import os
import json
from typing import Dict, Any

def test_dashboard_file():
    """Test that the dashboard file exists and has the correct content."""
    dashboard_path = "employer_dashboard.html"

    if not os.path.exists(dashboard_path):
        return False, "Dashboard file not found"

    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for key components
        checks = [
            ("HTML structure", "<html" in content and "</html>" in content),
            ("Employer Dashboard title", "Employer Dashboard" in content),
            ("API integration", "apiCall" in content and "API_BASE" in content),
            ("Authentication", "login()" in content and "authToken" in content),
            ("Job management", "loadJobs()" in content and "createJob()" in content),
            ("Application management", "loadRecentApplications()" in content),
            ("Candidate search", "searchCandidates()" in content),
            ("Dashboard stats", "loadDashboardStats()" in content),
            ("Auto-scoring", "autoScoreApplications()" in content),
            ("AI recommendations", "getAIRecommendations()" in content),
            ("Responsive design", "@media" in content),
            ("Modal dialogs", "modal" in content),
            ("Error handling", "try {" in content and "catch" in content)
        ]

        passed_checks = []
        failed_checks = []

        for check_name, result in checks:
            if result:
                passed_checks.append(check_name)
            else:
                failed_checks.append(check_name)

        return len(failed_checks) == 0, {
            "passed": passed_checks,
            "failed": failed_checks,
            "file_size": len(content)
        }

    except Exception as e:
        return False, f"Error reading dashboard file: {e}"

def test_api_endpoints():
    """Test that all required API endpoints are available in the router."""
    try:
        # Import the employer router to check endpoints
        import sys
        sys.path.append('.')
        from app.routers.employer import router

        # Get all routes from the router
        routes = router.routes
        endpoints = []

        for route in routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                for method in route.methods:
                    if method != 'HEAD':  # Skip HEAD methods
                        endpoints.append(f"{method} {route.path}")

        # Required endpoints for dashboard functionality
        required_endpoints = [
            "GET /dashboard/stats",
            "GET /jobs",
            "POST /jobs",
            "GET /jobs/{job_id}",
            "PUT /jobs/{job_id}",
            "DELETE /jobs/{job_id}",
            "GET /jobs/{job_id}/applications",
            "PUT /applications/{application_id}/status",
            "GET /candidates/search",
            "POST /jobs/{job_id}/auto-score-applications",
            "GET /jobs/{job_id}/ai-recommendations"
        ]

        missing_endpoints = []
        available_endpoints = []

        for required in required_endpoints:
            found = False
            for available in endpoints:
                if required in available or required.replace("{job_id}", ".*").replace("{application_id}", ".*") in available:
                    found = True
                    available_endpoints.append(required)
                    break

            if not found:
                missing_endpoints.append(required)

        return len(missing_endpoints) == 0, {
            "available_endpoints": available_endpoints,
            "missing_endpoints": missing_endpoints,
            "total_endpoints": len(endpoints)
        }

    except Exception as e:
        return False, f"Error checking API endpoints: {e}"

def test_main_app_integration():
    """Test that the main app has the dashboard route."""
    try:
        with open("main.py", 'r') as f:
            content = f.read()

        checks = [
            ("Dashboard route exists", "/employer-dashboard" in content),
            ("FileResponse import", "FileResponse" in content),
            ("Dashboard endpoint function", "async def employer_dashboard" in content),
            ("Dashboard info in root", '"employer_dashboard"' in content)
        ]

        passed = all(check[1] for check in checks)

        return passed, {
            "checks": checks,
            "has_dashboard_route": "/employer-dashboard" in content
        }

    except Exception as e:
        return False, f"Error checking main app: {e}"

def run_all_tests():
    """Run all dashboard tests."""
    print("🧪 Testing Employer Dashboard Integration")
    print("=" * 50)

    tests = [
        ("Dashboard File", test_dashboard_file),
        ("API Endpoints", test_api_endpoints),
        ("Main App Integration", test_main_app_integration)
    ]

    all_passed = True
    results = {}

    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            passed, details = test_func()
            results[test_name] = {"passed": passed, "details": details}

            if passed:
                print(f"✅ {test_name}: PASSED")
                if isinstance(details, dict):
                    for key, value in details.items():
                        if isinstance(value, list) and len(value) > 0:
                            print(f"   • {key}: {len(value)} items")
                        elif isinstance(value, (int, str)):
                            print(f"   • {key}: {value}")
            else:
                print(f"❌ {test_name}: FAILED")
                print(f"   Error: {details}")
                all_passed = False

        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            all_passed = False
            results[test_name] = {"passed": False, "details": str(e)}

    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Dashboard Features Available:")
        print("   • Employer authentication")
        print("   • Dashboard statistics")
        print("   • Job posting management")
        print("   • Application review")
        print("   • Candidate search")
        print("   • AI-powered matching")
        print("   • Auto-scoring applications")
        print("   • AI recommendations")
        print("   • Responsive design")

        print("\n🚀 To access the dashboard:")
        print("   1. Start the server: python3 main.py")
        print("   2. Open browser: http://localhost:8000/employer-dashboard")
        print("   3. Login with employer credentials")

    else:
        print("❌ Some tests failed. Please check the errors above.")

    return all_passed, results

if __name__ == "__main__":
    success, test_results = run_all_tests()
    exit_code = 0 if success else 1
    exit(exit_code)