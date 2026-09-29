import os
import sys
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_routes_exist_and_empty_validation():
    print("Testing Root & Validation...")
    
    # 1. GET /
    res = client.get("/")
    assert res.status_code == 200, f"GET / failed: {res.status_code}"
    assert "EduGenie" in res.text
    print("[PASS] GET / passed")

    # 2. GET /api/status
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["api_configured"] is True
    print("[PASS] GET /api/status passed")

    # 3. Empty validation on all endpoints
    res = client.post("/qa", json={"question": "   "})
    assert res.status_code == 422
    print("[PASS] POST /qa empty validation passed")

    res = client.post("/explain", json={"concept": "   "})
    assert res.status_code == 422
    print("[PASS] POST /explain empty validation passed")

    res = client.post("/quiz", json={"topic_or_passage": "   "})
    assert res.status_code == 422
    print("[PASS] POST /quiz empty validation passed")

    res = client.post("/summarize", json={"text": "short"})
    assert res.status_code == 422
    print("[PASS] POST /summarize validation passed")

    res = client.post("/learn/recommendations", json={"topic": "   "})
    assert res.status_code == 422
    print("[PASS] POST /learn/recommendations validation passed")

def test_live_ai_endpoints():
    import time
    print("\nTesting Live AI Endpoints with Gemini...")

    # 1. POST /qa
    print("1. Testing /qa...")
    res = client.post("/qa", json={"question": "Which is the largest ocean?"})
    assert res.status_code == 200, f"/qa failed: {res.text}"
    qa_data = res.json()
    assert "Pacific" in qa_data["answer"]
    print(f"[PASS] /qa passed")

    time.sleep(2)

    # 2. POST /explain
    print("2. Testing /explain...")
    res = client.post("/explain", json={"concept": "Pythagoras Theorem", "level": "beginner"})
    assert res.status_code == 200, f"/explain failed: {res.text}"
    exp_data = res.json()
    assert exp_data["simple_definition"]
    assert len(exp_data["step_by_step"]) > 0
    assert len(exp_data["key_points"]) > 0
    print(f"[PASS] /explain passed")

    time.sleep(2)

    # 3. POST /quiz
    print("3. Testing /quiz...")
    res = client.post("/quiz", json={"topic_or_passage": "Photosynthesis"})
    assert res.status_code == 200, f"/quiz failed: {res.text}"
    quiz_data = res.json()
    assert len(quiz_data["questions"]) == 3, f"Expected 3 questions, got {len(quiz_data['questions'])}"
    for idx, q in enumerate(quiz_data["questions"]):
        assert len(q["options"]) == 4, f"Question {idx+1} does not have 4 options"
        assert q["correct_answer"] in q["options"]
        assert q["explanation"]
    print(f"[PASS] /quiz passed with exactly 3 MCQs (4 options each)!")

    time.sleep(2)

    # 4. POST /summarize
    print("4. Testing /summarize...")
    solar_sample = (
        "The Solar System is the gravitationally bound system of the Sun and the objects that orbit it. "
        "It formed 4.6 billion years ago from the gravitational collapse of a giant interstellar molecular cloud. "
        "The vast majority of the system's mass is in the Sun, with the majority of the remaining mass contained in Jupiter. "
        "The four inner system planets—Mercury, Venus, Earth, and Mars—are terrestrial planets, being composed primarily of rock and metal."
    )
    res = client.post("/summarize", json={"text": solar_sample})
    assert res.status_code == 200, f"/summarize failed: {res.text}"
    sum_data = res.json()
    assert sum_data["summary"]
    assert len(sum_data["key_points"]) > 0
    assert sum_data["original_word_count"] > 0
    print(f"[PASS] /summarize passed (saved {sum_data['compression_ratio_pct']}%)")

    time.sleep(2)

    # 5. POST /learn/recommendations
    print("5. Testing /learn/recommendations...")
    res = client.post("/learn/recommendations", json={"topic": "SQL", "current_level": "Beginner"})
    assert res.status_code == 200, f"/learn/recommendations failed: {res.text}"
    learn_data = res.json()
    assert learn_data["beginner"]["what_to_learn"]
    assert learn_data["intermediate"]["what_to_learn"]
    assert learn_data["advanced"]["what_to_learn"]
    assert len(learn_data["projects_exercises"]) > 0
    print(f"[PASS] /learn/recommendations passed")

if __name__ == "__main__":
    test_routes_exist_and_empty_validation()
    test_live_ai_endpoints()
    print("\n[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!")
